# ISEC System Changes Summary

## Overview
This document summarizes all changes made to the ISEC (Índice de Sensibilidad al Error Categórico) system to implement metadata filtering functionality and improve output formatting.

## Changes Made

### 1. Metadata Filtering Implementation

#### A. For `Distancia_Semantica.py` (Semantic Distance Calculator)
- **Already had metadata filtering**: The file already contained full metadata filtering functionality
- **Methods updated**:
  - `find_closest_sentence()`: Already supported `exclude_same_group` and `exclude_same_subgroup` parameters
  - `find_top_k_semantic_matches()`: Already supported metadata filtering parameters
- **Main function**: Already demonstrated filtering when group data is available
- **No changes needed**: Full functionality was already implemented

#### B. For `matriz_costo_caracteres.py` (Levenshtein-Damerau Calculator)
- **Updated `load_sentences_from_excel()` function**: Now loads group and subgroup metadata from Excel files
- **Added `calculate_distances_with_filtering()` method**: New method to calculate edit distances with optional group/subgroup exclusion
- **Updated main function**: Now demonstrates metadata filtering functionality when group/subgroup data is available
- **Preserved existing functionality**: Kept original `calculate_all_distances()` method for all-to-all comparisons

#### C. For `ISEC.py` (ISEC Calculator)
- **Updated `load_sentences()` method**: Now properly loads and stores metadata list
- **Integrated filtering**: Uses `Config.SAME_GROUP_EXCLUSION` and `Config.SAME_SUBGROUP_EXCLUSION` settings
- **Semantic filtering**: Automatically applies metadata filtering when finding top k semantic matches

### 2. Output Format Improvements

#### A. Removed Aggregated Metrics
- **Removed from `ISECResult` class**:
  - `avg_semantic_distance: float`
  - `avg_cost_distance: float`
  - `avg_isec_score: float`
  - `isec_score: float`
- **Simplified `calculate_isec()` method**: Now only calculates per-match data
- **Updated print methods**: Removed aggregated metric displays
- **Excel export**: Removed aggregated columns

#### B. Added Matched Sentence Frequency
- **Excel export**: Added `Matched_Frequency` column showing frequency of matched sentences
- **Print output**: Added matched frequency display in `print_result()` method
- **Data structure**: Each match now includes complete frequency information

#### C. Per-Pair ISEC Calculation
- **Independent calculations**: Each Excel row now shows independent ISEC calculation for a specific sentence-match pair
- **No cross-row metrics**: Removed all aggregated calculations that combined data across rows
- **Clean output**: Each row contains all necessary information for analysis

### 3. Configuration Updates

#### A. `.env` File Additions
- **Group/Subgroup columns**: Added configuration for metadata columns
  - `SENTENCES_GROUP_COLUMN=Group`
  - `SENTENCES_SUBGROUP_COLUMN=Subgroup`
- **Filtering settings**: Added control for metadata filtering
  - `SAME_GROUP_EXCLUSION=False`
  - `SAME_SUBGROUP_EXCLUSION=False`

#### B. `config.py` Updates
- **New getter functions**: Added `get_string_env()` and `get_bool_env()` for configuration
- **Configuration class**: Added new settings to `Config` class
- **Display method**: Updated to show filtering configuration

### 4. New Excel Output Format

#### Columns in `ISEC_Results.xlsx`:
1. `Sentence` - Source sentence
2. `Sentence_Group` - Group of source sentence
3. `Frequency` - Frequency of source sentence
4. `FMN` - Frequency Median Normalized
5. `Match_Rank` - Rank of this match (1 to k)
6. `Matched_Sentence` - The matched sentence
7. `Matched_Sentence_Group` - Group of matched sentence
8. `Matched_Frequency` - Frequency of matched sentence
9. `Semantic_Distance` - Semantic distance between the pair
10. `Cost_Distance` - Edit cost distance between the pair
11. `ISEC_Score` - ISEC score for this specific pair

#### Key Features:
- **Independent rows**: Each row is a complete ISEC calculation for one pair
- **Complete frequency info**: Both source and matched sentence frequencies
- **Metadata for filtering**: Group information for both sentences
- **No aggregation**: Only per-pair calculations

### 5. Documentation Updates

#### A. `ISEC_README.md`
- Updated output format examples
- Updated API reference for `ISECResult` class
- Added metadata filtering information
- Updated Excel export format documentation

#### B. `SEMANTIC_DISTANCE_README.md`
- Enhanced metadata filtering documentation
- Added configuration-based filtering examples
- Updated API reference with filtering parameters
- Added filtering behavior explanations

#### C. `COST_MATRIX_README.md`
- Added metadata filtering section
- Updated Excel file format documentation
- Added filtering configuration instructions
- Added related documentation links

#### D. `GUIDE.md`
- Complete rewrite with new features
- Added comprehensive examples
- Added system component descriptions
- Added configuration instructions
- Added Excel output format documentation

### 6. Test Files Created

#### A. `test_matched_frequency.py`
- Tests matched frequency functionality
- Verifies Excel export includes `Matched_Frequency` column
- Tests print output includes matched frequency
- Validates data structure correctness

#### B. Existing test files updated:
- `test_filtering.py`: Already tested metadata filtering
- `test_basic.py`: Basic functionality tests
- `test_parameter_sensitivity.py`: Parameter sensitivity tests

## Technical Implementation Details

### Metadata Filtering Logic

#### Semantic Distance Calculator (`Distancia_Semantica.py`):
- Uses ChromaDB `where` clauses for filtering
- Query: `where={"group": {"$ne": query_group}}` for group exclusion
- Efficient database-level filtering
- Returns `None` if all matches filtered out

#### Edit Cost Calculator (`matriz_costo_caracteres.py`):
- Python-level filtering during distance calculation
- Checks metadata before computing distances
- Skips comparisons where group/subgroup matches exclusion criteria
- Returns filtered list of `DistanceResult` objects

#### ISEC Calculator (`ISEC.py`):
- Uses semantic calculator's filtering capabilities
- Applies filtering when finding top k semantic matches
- Configuration-driven via `.env` settings
- Transparent to user - automatic application

### Frequency Integration

#### Data Flow:
1. Excel file loads sentences with metadata
2. Frequencies extracted from metadata for backward compatibility
3. Both source and matched frequencies stored
4. Displayed in print output and Excel export
5. Used in ISEC calculations (FMN based on source frequency)

#### Excel Processing:
- `load_sentences_from_excel()` handles duplicate sentences
- Merges frequencies by summing
- Keeps first group/subgroup value for duplicates
- Returns unique sentences with merged metadata

## Configuration Settings Summary

### File Paths:
- `SENTENCES_FILE=Clases.xlsx`
- `CUSTOM_COSTS_FILE=Custom_cost.xlsx`
- `ISEC_OUTPUT_FILE=ISEC_Results.xlsx`

### Column Names:
- `SENTENCES_NAME_COLUMN=Name`
- `SENTENCES_FREQUENCY_COLUMN=Frequency`
- `SENTENCES_GROUP_COLUMN=Group`
- `SENTENCES_SUBGROUP_COLUMN=Subgroup`

### Filtering Control:
- `SAME_GROUP_EXCLUSION=False` (Set to `True` to exclude same-group matches)
- `SAME_SUBGROUP_EXCLUSION=False` (Set to `True` to exclude same-subgroup matches)

### Operation Costs:
- `DEFAULT_SUBSTITUTION_COST=1.0`
- `DEFAULT_INSERTION_COST=1.0`
- `DEFAULT_DELETION_COST=1.0`
- `DEFAULT_TRANSPOSITION_COST=1.0`
- `COST_FACTOR_PENALIZATION=0.1`

### ISEC Settings:
- `ISEC_SEMANTIC_WEIGHT=0.4`
- `ISEC_TOP_K_MATCHES=3`

## Usage Examples

### Enable Metadata Filtering:
```bash
# In .env file:
SAME_GROUP_EXCLUSION=True
SAME_SUBGROUP_EXCLUSION=False
```

### Excel File Format:
```excel
| Name       | Frequency | Group | Subgroup |
|------------|-----------|-------|----------|
| Sentence1  | 100       | A     | A1       |
| Sentence2  | 50        | A     | A2       |
| Sentence3  | 75        | B     | B1       |
```

### Run System:
```bash
# Semantic distance with filtering
python Distancia_Semantica.py

# Edit distance with filtering
python matriz_costo_caracteres.py

# ISEC calculation with per-pair results
python ISEC.py
```

## Benefits of Changes

1. **Metadata Filtering**: Allows exclusion of matches within same categories
2. **Clean Output**: Per-pair calculations without confusing aggregates
3. **Complete Information**: Both source and matched frequencies available
4. **Configuration-Driven**: Easy control via `.env` file
5. **Backward Compatible**: Existing functionality preserved
6. **Better Analysis**: Independent rows allow detailed pair-wise analysis
7. **Consistent System**: All components use same metadata format

## Files Modified

### Core Implementation Files:
- `ISEC/ISEC.py` - Main ISEC calculator with per-pair calculations
- `ISEC/matriz_costo_caracteres.py` - Edit distance calculator with filtering
- `ISEC/Distancia_Semantica.py` - Semantic distance calculator (already had filtering)
- `ISEC/config.py` - Configuration management

### Documentation Files:
- `ISEC/ISEC_README.md` - Updated with new output format
- `ISEC/SEMANTIC_DISTANCE_README.md` - Enhanced filtering documentation
- `ISEC/COST_MATRIX_README.md` - Added filtering features
- `ISEC/GUIDE.md` - Complete rewrite with new features
- `ISEC/CHANGES_SUMMARY.md` - This summary document

### Test Files:
- `ISEC/test_matched_frequency.py` - New test for frequency functionality
- `ISEC/test_filtering.py` - Existing test for metadata filtering

## Migration Notes

### For Existing Users:
1. **No breaking changes**: Existing functionality preserved
2. **New columns in Excel**: Output includes additional columns
3. **Optional filtering**: Disabled by default, enable via `.env`
4. **Same input format**: Excel files can now include Group/Subgroup columns

### For New Users:
1. **Start with GUIDE.md**: Comprehensive getting started guide
2. **Configure `.env`**: Set up filtering preferences
3. **Add metadata columns**: Optional Group/Subgroup columns in Excel
4. **Use test files**: Verify functionality with test scripts

## Future Considerations

1. **Additional Filtering Criteria**: Could add more metadata-based filters
2. **Performance Optimization**: Large datasets may need optimization
3. **Visualization Tools**: Could add visualization for filtered results
4. **Batch Processing**: Support for processing multiple files
5. **Advanced Metrics**: Additional linguistic analysis metrics

## Conclusion

The ISEC system has been enhanced with comprehensive metadata filtering capabilities and improved output formatting. The changes provide:

1. **Flexible filtering** based on group/subgroup metadata
2. **Clean, per-pair calculations** without aggregated metrics
3. **Complete frequency information** for both sentences in each pair
4. **Configuration-driven behavior** via `.env` file
5. **Comprehensive documentation** for all new features

The system now provides more detailed and flexible analysis capabilities while maintaining backward compatibility and ease of use.