# Linear Sampling Algorithm

The LSA is a sampling-based strategy created by Flávio Mota Medeiros to detect configuration-related bugs in Software Product Lines. 
The strategy groups three sampling methods (one enabled, one disabled, most enabled disabled) to generate the configurations that need to be tested.

## Running

```
python main.py -i input.json -o output.json
```

## Input Example

```
{
    "features": [
        { "code": "1", "name": "Feature 1" },
        { "code": "2", "name": "Feature 2" }
    ]
}
```

## Authors

* **Gleyberson Andrade** - [gleybersonandrade](https://github.com/gleybersonandrade)

## References

* An Approach to Safely Evolve Preprocessor-Based C Program Families (MEDEIROS; Flavio, 2016)

## License

This project is licensed under the MIT License.

