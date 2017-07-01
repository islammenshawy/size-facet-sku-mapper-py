# size-facet-sku-mapper-py
This Application is a built as a python implementation of the nodejs application under https://github.com/islammenshawy/size-facet-sku-mapper

The mapper will utilize the product feed to generate another file that will contain the size facets mapping with SKU to ease 
the mapping of the SFCs to SKU records

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. Also included a shell script that will install the necessary dependencies.

### Prerequisites for running in local
Python installed

### Output files and format
The application will generate 2 files one with the SKUs that got mapped that are inventory available with [_SFCs] in the name and 
another file with the SKUs that didn't get mapped with name ending with [_SFCs_Non]

The non mapped SKUs are not associated with any SFCs and for testing purpose on search page

Header information:
SKU|WebModel|Dimension|Variance|size1|size2|Dimension|

### Examples run with sample file
```
./sfc_mapper.sh ${File_Name}
Ex: ./sfc_mapper.sh on_us_ol_fullText 
```
