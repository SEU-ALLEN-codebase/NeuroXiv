import json
import re


def load_search_conditions(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def extract_search_conditions(json_data):
    search_conditions = {}

    def process_node(node):
        if 'querry_name' in node:
            query_name = node['querry_name']
            if node['type'] == 'range':
                min_val = node.get('default_min', 0)
                max_val = node.get('default_max', 1)
                search_conditions[query_name] = {'type': 'range', 'default': [min_val, max_val]}
            elif node['type'] == 'category' or node['type'] == 'binary':
                candidates = node.get('candidates', [])
                search_conditions[query_name] = {'type': node['type'], 'candidates': candidates}
        if 'children' in node:
            for child in node['children']:
                process_node(child)

    for region in json_data['children']:
        process_node(region)

    return search_conditions


def parse_query(query, search_conditions):
    parsed_conditions = {}

    # Parse conditions based on search_conditions
    for key, condition in search_conditions.items():
        # Handle range type conditions
        if condition['type'] == 'range':
            range_match = re.search(rf'{key.replace("_", " ")} (less than|more than|between) (\d+)', query)
            if range_match:
                range_type = range_match.group(1)
                value = float(range_match.group(2))
                if range_type == 'less than':
                    parsed_conditions[key] = [condition['default'][0], value]
                elif range_type == 'more than':
                    parsed_conditions[key] = [value, condition['default'][1]]
                elif range_type == 'between':
                    # For 'between' case, extract both values if provided
                    between_match = re.search(rf'{key.replace("_", " ")} between (\d+) and (\d+)', query)
                    if between_match:
                        min_value = float(between_match.group(1))
                        max_value = float(between_match.group(2))
                        parsed_conditions[key] = [min_value, max_value]
                    else:
                        parsed_conditions[key] = condition['default']
            else:
                # If no specific value is detected, use default range
                if re.search(rf'{key.replace("_", " ")}', query):
                    parsed_conditions[key] = condition['default']

        # Handle category and binary type conditions
        elif condition['type'] in ['category', 'binary']:
            for candidate in condition['candidates']:
                if re.search(rf'\b{candidate}\b', query, re.IGNORECASE):
                    if key not in parsed_conditions:
                        parsed_conditions[key] = []
                    parsed_conditions[key].append(candidate)

    return parsed_conditions


if __name__ == "__main__":
    query = "find MOp neurons whose dendrite total length longer than 1000"
    json_data = load_search_conditions('./SearchCondition/search_conditions.json')
    search_conditions = extract_search_conditions(json_data)
    parsed_conditions = parse_query(query, search_conditions)
    print(json.dumps(parsed_conditions, indent=2))
