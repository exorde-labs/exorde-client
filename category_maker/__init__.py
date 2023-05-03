
import json

#######################################
# Parameters

output_top_level_categories = [
   "Arts and Entertainment", 
   "Lifestyle and Traditions", 
   "Science and Research", 
   "Technology and Innovation",
   "Economy and Finance", 
   "Politics and Society", 
   "Nature and Environment",
   "Business and Industry", 
   "Education and Learning", 
   "Religion and Spirituality",
   "Health and Wellness",
   "Travel and Exploration", 
   "Law and Justice", 
   "Media and Communication", 
   "Sports and Recreation"]

rename_dict = {
    "Finance": "Economy and Finance",
    "Business and Industrial": "Business and Industry",
    "Health": "Health and Wellness",
    "Jobs and Education": "Education and Learning",
    "Science": "Science and Research",
    "Sports": "Sports and Recreation",
    "Travel": "Travel and Exploration",
    "Law and Government": "Law and Justice",    
    "News" : "Media and Communication"
}

combine_dict = {
    "Nature and Environment": ["Earth Sciences", "Ecology and Environment", "Pets and Animals"],
    "Business and Industry": ["Autos and Vehicles", "Shopping"],
    "Health and Wellness": ["Beauty and Fitness"],
    "Economy and Finance": ["Real Estate"],
    "Lifestyle and Traditions": ["Hobbies and Leisure", "Home and Garden"],
    "Media and Communication": ["News"],
    "Technology and Innovation": ["Computers and Electronics", "Internet and Telecom"],
    "Sports and Recreation": ["Games"],
    "Politics and Society": ["People and Society", "Politics", "Online Communities"],
    "Education and Learning": ["Books and Literature"],
    "Religion and Spirituality": ["Religion and Belief"],
    "Arts and Entertainment": ["Celebrities and Entertainment News", "Entertainment Industry", "Events and Listings", "Humor", "Movies", "Music and Audio"]
}

hardcoded_hierarchy = {
    "Cryptocurrency":{
        "Collectibles and NFT":{
            "Digital Art" : {},
            "Domain Name" : {},
            "Gaming cards" : {},
            "Marketplace" : {}
        },
        "Tokens":{
            "Utility Tokens" : {},
            "Stablecoins" : {},
            "DeFi Protocols" : {},
            "Exchanges token" : {}
        },
        "Blockchain wallet":{
            "Metamask",
            "Ledger hardware"
        },
        "Decentralized Protocols": {}
    }
}
# Define the high-level categories to keep
used_categories = output_top_level_categories #optional

max_depth = 1

#######################################
# recursive category parser
def parse_category(node):
    name = node.get("name", "")
    name = name.replace('and', 'and')

    children = node.get("children", [])

    if not children:
        return name, None

    result = {}
    for child in children:
        child_name, child_data = parse_category(child)
        if child_data is not None:
            result[child_name] = child_data
        else:
            result[child_name] = {}

    return name, result

def rename_categories(data, rename_dict):
    renamed_data = {}

    for key, value in data.items():
        if key in rename_dict:
            new_key = rename_dict[key]
            renamed_data[new_key] = value
        else:
            renamed_data[key] = value

    return renamed_data

def find_and_combine_category(data, category_to_find):
    if isinstance(data, list):
        new_list = []
        for item in data:
            result = find_and_combine_category(item, category_to_find)
            if result is not None:
                new_list.append(result)
        return new_list if new_list else None

    if category_to_find in data:
        return data[category_to_find]

    new_dict = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result = find_and_combine_category(value, category_to_find)
            if result is not None:
                new_dict[key] = result
        elif isinstance(value, list):
            result = find_and_combine_category(value, category_to_find)
            if result is not None:
                new_dict[key] = result
        else:
            new_dict[key] = value

    return new_dict if new_dict else None

def combine_categories(final_output, parsed_data, combined_categories_dict):
    for target_category, sources in combined_categories_dict.items():
        for source_category in sources:
            source_data = find_and_combine_category(parsed_data, source_category)
            if source_data is not None:
                if target_category in final_output:
                    final_output[target_category].update({source_category: source_data})
                else:
                    final_output[target_category] = {source_category: source_data}
            else:
                print(f"Category '{source_category}' not found in parsed_data")
    final_output.update(parsed_data)
    return final_output

def add_hardcoded_hierarchy(data, hierarchy, parent_category):
    if parent_category not in data:
        return data

    for category, children in hierarchy.items():
        if children:
            if category in data[parent_category]:
                add_hardcoded_hierarchy(data[parent_category][category], children, category)
            else:
                data[parent_category][category] = children
        else:
            data[parent_category][category] = {}

    return data

# recursive output nested parser with pruning
def prune_data(data, max_depth, categories_to_keep=None, current_depth=0):
    pruned_data = {}
    for key, value in data.items():
        if categories_to_keep is None or key in categories_to_keep:
            if value and current_depth < max_depth:
                pruned_data[key] = prune_data(value, max_depth, None, current_depth + 1)
            else:
                pruned_data[key] = {}
    return pruned_data

# recursive counter for stats
def analyze_data(data, current_depth=0, level_count=None):
    if level_count is None:
        level_count = {}
    
    if current_depth not in level_count:
        level_count[current_depth] = 0

    leaf_count = 0
    for key, value in data.items():
        level_count[current_depth] += 1
        if value:
            leaves, level_count = analyze_data(value, current_depth + 1, level_count)
            leaf_count += leaves
        else:
            leaf_count += 1

    return leaf_count, level_count

# stats printer for a nested json
def compute_and_print_stats(pruned_data):
    leaf_count, level_count = analyze_data(pruned_data)
    max_level = max(level_count.keys())
    total_categories = sum(level_count.values())

    print(f"Total levels: {max_level + 1}")
    print("Categories per level:")
    for level, count in level_count.items():
        print(f"  Level {level}: {count} categories")

    print(f"Average categories per level: {total_categories / (max_level + 1):.2f}")
    print(f"Total leaf nodes: {leaf_count}")



def parse_json_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    return parse_category(data)

# Read the JSON file and parse it
file_name = "google_trends_categories.json"
_, parsed_data = parse_json_file(file_name)

# Combine the subcategories as children of the appointed categories in parsed_data
combined_data = combine_categories({}, parsed_data, combine_dict)

# Rename the top-level categories in combined_data
renamed_data = rename_categories(combined_data, rename_dict)

# Add hardcoded hierarchy to "Economy and Finance"
renamed_data = add_hardcoded_hierarchy(renamed_data, hardcoded_hierarchy, "Economy and Finance")
renamed_data = add_hardcoded_hierarchy(renamed_data, hardcoded_hierarchy, "Technology and Innovation")

# Create an empty dictionary with the desired top-level categories and update it with the renamed_data
final_output = {category: {} for category in output_top_level_categories}
final_output.update(renamed_data)


# Prune the final_output data
pruned_data = prune_data(final_output, max_depth=max_depth, categories_to_keep=used_categories)


# Write the formatted data to a JSON file
with open("output_nested_categories.json", "w") as outfile:
    json.dump(pruned_data, outfile, indent=3)

# Analyze the pruned data and print the stats
compute_and_print_stats(pruned_data)
