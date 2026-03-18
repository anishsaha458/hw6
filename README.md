I want to use SQL as a database to store information about recipes where the user types in a recipe and is able to access the recipe as necesasry. I want to use a CLI to fully implement the SQL database that stores recipe information.

I specifically chose recipes as I want to learn how to bake and cook. I think creating a database for recipes would be a great way to incentivize myself to use the recipes and their information. Using SQL databases to store information is fascinating and an implementation of SQL for recipes is similar to creating a time capsule. It will never be erased and I can continue to add on as time goes on and access as I need knowing that the database will always store the information.

The app uses a single recipes table in recipes.db

id intger pk auto-incremented unique identifier
name text recipe name (required)
category text breakfast, lunch, dinner, dessert, snack
ingredients text comma-separated/ free-form list
instructions text step-by-step instructions
prep_time integer preparation time
rating integer personal rating 1-10
notes text notes

Create- Adds a brand new recipe to the database. Prompted to enter the recipe name, ingredients, instructions, and optional prep time, a rating between 1-10, and any personal notes. The recipe is permanenetly saved to recipes.db

Read(All)- retrieves every recipe stored in the database and displays them in a table sorted alphabetically by name

Read(search/filter) - queries the database with optional filters. narrow results by category, set a minimum star rating, and choose how to sort the results

Read(Detail) - Fetches and displays the full record for a single recipe by ID

Update - Modifies an existing recipe in the database. select recipe by ID, then show current value of each filed

Delete- permanently removes an entry to the database by ID. The app shows the recipe name and asks for confirmation before deleting.


To run the app
-enssure that python is installed (python 3.7 or higher is required)
run python.py