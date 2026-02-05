@app.post("/api/pair-detail")
async def get_pair_detail(req: PairDetailRequest):
    """Get detailed transformation analysis for a specific sentence pair"""
    
    # Update params (same as calculate endpoint)
    params = req.params
    
    if "semantic_weight" in params:
        global_calculator.semantic_weight = params["semantic_weight"]
        global_calculator.morphologic_weight = 1.0 - params["semantic_weight"]
        
    cc = global_calculator.cost_calculator
    changed = False
    
    if "substitution" in params and params["substitution"] != cc.default_substitution_cost:
        cc.default_substitution_cost = params["substitution"]
        changed = True
    if "insertion" in params and params["insertion"] != cc.default_insertion_cost:
        cc.default_insertion_cost = params["insertion"]
        changed = True
    if "deletion" in params and params["deletion"] != cc.default_deletion_cost:
        cc.default_deletion_cost = params["deletion"]
        changed = True
    if "transposition" in params and params["transposition"] != cc.default_transposition_cost:
        cc.default_transposition_cost = params["transposition"]
        changed = True
        
    if changed:
        cc.setup_characters(all_chars)
        
    if "cost_factor" in params:
        Config.COST_FACTOR_PENALIZATION = params["cost_factor"]
    
    # Calculate edit distance with operations
    cost_result = global_calculator.cost_calculator.calculate_edit_distance(
        req.sentence1, req.sentence2
    )
    
    # Calculate semantic distance
    semantic_matches = global_calculator.semantic_calculator.find_top_k_semantic_matches(
        req.sentence1, k=1, exclude_same_group=False, exclude_same_subgroup=False
    )
    
    # Find the semantic distance for sentence2
    semantic_distance = 0.0
    for sent, dist, _ in semantic_matches:
        if sent == req.sentence2:
            semantic_distance = dist
            break
    
    # If not found in top matches, calculate directly
    if semantic_distance == 0.0:
        try:
            # Get embeddings for both sentences
            emb1 = global_calculator.semantic_calculator.get_embedding(req.sentence1)
            emb2 = global_calculator.semantic_calculator.get_embedding(req.sentence2)
            # Calculate cosine distance
            import numpy as np
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            semantic_distance = 1.0 - similarity
        except:
            semantic_distance = 0.0
    
    # Get frequencies
    freq1 = global_calculator.frequencies.get(req.sentence1, 1)
    freq2 = global_calculator.frequencies.get(req.sentence2, 1)
    
    # Calculate FMN for sentence1
    import math
    if Config.ISEC_FREQUENCY_SCALING_ENABLED:
        log_base = Config.ISEC_FREQUENCY_LOG_BASE if Config.ISEC_FREQUENCY_LOG_BASE > 1 else math.e
        f = max(freq1, 1e-10)
        if log_base == math.e:
            fmn = math.log(f) + 1
        else:
            fmn = math.log(f, log_base) + 1
    else:
        fmn = float(freq1)
    
    # Calculate ISEC score for this pair
    weighted_distance = (
        global_calculator.semantic_weight * semantic_distance +
        global_calculator.morphologic_weight * cost_result.penalized_distance
    )
    
    if weighted_distance > 0:
        isec_score = fmn / weighted_distance
    else:
        isec_score = float('inf')
    
    # Format operations
    operations = []
    for op in cost_result.operations:
        operations.append({
            "type": op.op_type,
            "from_char": op.from_char,
            "to_char": op.to_char,
            "cost": op.cost
        })
    
    # Count operations by type
    op_counts = {
        "match": sum(1 for op in cost_result.operations if op.op_type == "match"),
        "substitute": sum(1 for op in cost_result.operations if op.op_type == "substitute"),
        "insert": sum(1 for op in cost_result.operations if op.op_type == "insert"),
        "delete": sum(1 for op in cost_result.operations if op.op_type == "delete"),
        "transpose": sum(1 for op in cost_result.operations if op.op_type == "transpose")
    }
    
    return {
        "sentence1": req.sentence1,
        "sentence2": req.sentence2,
        "frequency1": freq1,
        "frequency2": freq2,
        "group1": global_calculator.metadata_map.get(req.sentence1, {}).get("group", "N/A"),
        "group2": global_calculator.metadata_map.get(req.sentence2, {}).get("group", "N/A"),
        "semantic_distance": semantic_distance,
        "cost_distance": {
            "total": cost_result.total_distance,
            "average": cost_result.average_cost,
            "sum_edit_costs": cost_result.sum_edit_costs,
            "penalized": cost_result.penalized_distance
        },
        "fmn": fmn,
        "isec_score": isec_score if isec_score != float('inf') else 0,
        "operations": operations,
        "operation_counts": op_counts,
        "num_operations": cost_result.num_operations
    }
