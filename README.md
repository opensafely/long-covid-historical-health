# Long COVID burden and risk factors in 10 UK longitudinal studies and electronic health records

This is the code and configuration for our paper, Long COVID burden and risk factors in 10 UK longitudinal studies and electronic health records

* The paper is [here](https://doi.org/10.1038/s41467-022-30836-0)
* The pre-printed version is [here](https://doi.org/10.1101/2021.06.24.21259277)
* If you are interested in how we defined our variables, take a look at the [study definition](analysis/study_definition.py); this is written in `python`, but non-programmers should be able to understand what is going on there
* If you are interested in how we defined our code lists, look in the [codelists folder](./codelists/).
* Developers and epidemiologists interested in the framework should review [the OpenSAFELY documentation](https://docs.opensafely.org)

# About the OpenSAFELY framework

The OpenSAFELY framework is a secure analytics platform for
electronic health records research in the NHS.

Instead of requesting access for slices of patient data and
transporting them elsewhere for analysis, the framework supports
developing analytics against dummy data, and then running against the
real data *within the same infrastructure that the data is stored*.
Read more at [OpenSAFELY.org](https://opensafely.org).
