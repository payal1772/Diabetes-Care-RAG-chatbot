import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "datasets"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

# Load CSV files
food_df = pd.read_csv(DATASET_DIR / "food.csv")
food_nutrient_df = pd.read_csv(DATASET_DIR / "food_nutrient.csv", low_memory=False)
nutrient_df = pd.read_csv(DATASET_DIR / "nutrient.csv")

# Keep only important nutrients
important_nutrients = [
    "Carbohydrate, by difference",
    "Protein",
    "Fiber, total dietary",
    "Sugars, total including NLEA",
    "Energy"
]

important_nutrient_ids = nutrient_df[
    nutrient_df["name"].isin(important_nutrients)
][["id", "name"]]

# Merge nutrient names
merged_df = food_nutrient_df.merge(
    important_nutrient_ids,
    left_on="nutrient_id",
    right_on="id"
)

# Merge food names
merged_df = merged_df.merge(
    food_df[["fdc_id", "description"]],
    left_on="fdc_id",
    right_on="fdc_id"
)

food_knowledge = []

# Group by food
for food_name, group in merged_df.groupby("description"):

    text = f"Food: {food_name}\n"

    for _, row in group.iterrows():
        nutrient_name = row["name"]
        amount = row["amount"]

        text += f"{nutrient_name}: {amount}\n"

    food_knowledge.append(text)

# Save knowledge file
with open(KNOWLEDGE_BASE_DIR / "food_knowledge.txt", "w", encoding="utf-8") as file:
    file.write("\n\n".join(food_knowledge))

print("Food knowledge base created successfully.")
