import os

path = '/Users/maurobenetti/Documents/PhD/Python/ISEC/app/static/index.html'
with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    if "pair-summary-label\">FMN {{" in lines[i] and "? '(log" in lines[i] and i+1 < len(lines):
        # Merge this line with the next one
        current_line = lines[i].rstrip()
        next_line = lines[i+1].lstrip()
        merged = current_line + " " + next_line
        new_lines.append(merged)
        i += 2
    else:
        new_lines.append(lines[i])
        i += 1

with open(path, 'w') as f:
    f.writelines(new_lines)
print("Fix applied.")
