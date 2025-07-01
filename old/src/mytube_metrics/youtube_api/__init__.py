# Used for making imports from the api package cleaner; contents are run the first time any module from the package is imported into program execution

# # main.py (some other file outside the package)
# from my_calculator import operations
# result = operations.add(5, 3) 

### VS

# # __init__.py in the my_calculator folder
# from .operations import add

# # main.py
# from my_calculator import add  # <-- So much cleaner!
# result = add(5, 3)
