# Linear Sampling Algorithm

The LSA is a sampling-based strategy created by Flávio Mota Medeiros to detect configuration-related bugs in Software Product Lines. 
The strategy groups three sampling methods (one enabled, one disabled, most enabled disabled) to generate the configurations that need to be tested.

## Running

The algorithm can be executed using one of the following instructions:

### Generate model

```
python main.py -p project_name -g project_path
```

*Parameters:*

 - **-p**: name of the project, used to name the model and features files;
 - **-g**: path of the project.

*Model Example:*

```
{
    "1": {
        "type": "Feature",
        "attr": "optional",
        "name": "A"
    },
    "2": {
        "type": "Feature",
        "attr": "optional",
        "name": "B"
    }
}
```

### Run LSA

```
python main.py -p project_name -i model.json -t type
```

*Parameters:*

 - **-p**: name of the project, used to name the result file;
 - **-i**: path of the model.
 - **-t**: type of strategy, can be:
   - **original**: Generate results basying only on features;
   - **any**: Generate results respecting the limitations of the model (only one product is created in decision making);
   - **all**: Generate results respecting the limitations of the model (all products are created in decision making);
   - **rand_original**: Same as the *original* type, but only 3 products are created;
   - **rand_any**: Same as the *any* type, but only 3 products are created;
   - **rand_all**: Same as the *all* type, but only 3 products are created.

## Authors

* **Gleyberson Andrade** - [gleybersonandrade](https://github.com/gleybersonandrade)

## References

* An Approach to Safely Evolve Preprocessor-Based C Program Families (MEDEIROS; Flavio, 2016)

## License

This project is licensed under the MIT License.
