import pandas as pd
import os
import sys
import time
import json

#Global Variables
categories_file_name = 'data/size_facet_categories.csv'
size_mapping_file_name = 'data/size_model_facets_mappings.csv'


# Function to build the SFC ids cache key
def buildSFCsCacheTagKey(departmentTag, productTypeTag, categoryGroupTag):
    return "{0}|{1}|{2}".format(departmentTag, productTypeTag, categoryGroupTag)

# Function to build size model key for size model cache
def buildSizeModelKey(sizeModel):
  return sizeModel

# Function to build the size facet breadCrumb
def buildSizeFacetBreadCrumb(row):
       sizeFacetWebName, sizeFacetDimName, variant, dimension, sizeFacetVar1Selected, sizeFacetVar2Selected \
        = row.SZ_FACET_WEB_NAME, row.SZ_FCT_DIM_NAME, row.SZ_VAR_NM, row.DIMENSION, row.SZ_FCT_VAL1_SLCTD, row.SZ_FCT_VAL2_SLCTD
       return "{0}|{1}|{2}|{3}|{4}".format(sizeFacetWebName, sizeFacetDimName, variant, sizeFacetVar1Selected
                                                 , sizeFacetVar2Selected)

# **********************************
# ********* Load SFC cache *********
# **********************************
def loadSizeFacetCache():
    sfc_start_time = time.time()
    print("--- Started loading SFCs cache. ---")
    tagsCache = {}
    sfc_data = pd.read_csv(categories_file_name, dtype = {
        "SZ_FCT_CATG_ID": str, "SZ_FCT_SORT_ORDER_NUMBER": str, "SZ_FCT_NUMBER_OF_DIM": str, "DIMENSION": str,
        "SZ_FCT_NAME": str, "SZ_FCT_ALPH_ALT_CTG_ID": str, "SZ_FCT_ALPH_ALT_CTG": str, "SZ_FACET_WEB_NAME": str,
        "SZ_DIM1_NAME": str, "SZ_DIM2_NAME": str, "SZ_VARIANT_SORT_ORDER": str, "SZ_FACET_DESCRIPTION": str,
        "SZ_FCT_VAL_NM": str, "SZ_FCT_VAL_NM_2": str, "COL_POS_NBR": str, "CATEGORY_GROUP_TAG_NAME": str,
        "DEPARTMENT_TAG_NAME": str, "PRODUCT_TYPE_TAG_NAME": str
    }).fillna('')
    for index, row in sfc_data.iterrows():
        #values from the spreadsheet
        categoryGroupTag, departmentTag, productTypeTag, rowSfctgId = \
            row.CATEGORY_GROUP_TAG_NAME, row.DEPARTMENT_TAG_NAME, row.PRODUCT_TYPE_TAG_NAME, row.SZ_FCT_CATG_ID
        tagsCachekey = buildSFCsCacheTagKey(departmentTag, productTypeTag, categoryGroupTag)
        tagsCacheValue = tagsCache.get(tagsCachekey)
        if tagsCacheValue is not None:
            alreadyExists = False
            for currentSfcId in tagsCacheValue:
                if currentSfcId == rowSfctgId:
                    alreadyExists = True
                    break
            if not alreadyExists:
                tagsCacheValue.append(rowSfctgId)
        else:
            cacheTagValueArray = []
            cacheTagValueArray.append(rowSfctgId)
            tagsCache[tagsCachekey]= cacheTagValueArray
    print("--- Took %s seconds to load SFCs cache. ---" % (time.time() - sfc_start_time))
    return tagsCache

# ********************************************
# ********* Load size model data *************
# ********************************************
def loadSizeModelCache():
    sz_mapp_start_time = time.time()
    print('--- Started loading size model cache. ---')
    sz_mapp_data = pd.read_csv(size_mapping_file_name, dtype = {
        "SZ_FCT_CATG_ID": str, "SZ_MDL_CD": str, "SZ_CD": str, "SZ_VAL_DATA_TYP_DESC": str, "DIMENSION": str,
        "SF_SRT_ORD_NBR": str, "SZ_FCT_CATG_ADMN_NM": str, "SZ_FACET_WEB_NAME": str, "SZ_FCT_DIM_NAME": str,
        "SF_SZ_SRT_ORD_NBR": str, "SZ_FCT_VAL1_SLCTD": str, "SZ_FCT_VAL2_SLCTD": str, "SZ_VAR_NM": str,
        "SZ_VAR_SRT_ORDR": str, "DIM_VAL_TXT": str, "DIM_VAL2_TXT": str, "DIM_VAL3_TXT": str
    }).fillna('')
    sizeModelCache = {}
    for index, row in sz_mapp_data.iterrows():
        # values from the spreadsheet
        rowSizeModel, rowsizeCode, rowsizeFacetName, dimension, sfcId = \
            row.SZ_MDL_CD, row.SZ_CD, row.SZ_FCT_CATG_ADMN_NM, row.DIMENSION, row.SZ_FCT_CATG_ID

        #Size facet id/Model cache logic
        cacheKey = buildSizeModelKey(rowSizeModel)
        cacheValue = sizeModelCache.get(cacheKey)
        currentBrdCrumb = buildSizeFacetBreadCrumb(row)

        #current Row from implementation.
        currentRow = {}
        currentRow['sfcId'] = str(sfcId)
        currentRow['sizeCode'] = str(rowsizeCode)
        currentRow['sizeFacetName'] = str(rowsizeFacetName)
        currentRow['dimension'] = str(dimension)
        currentRow['sizeFacetBreadCrumb'] = str(currentBrdCrumb)

        if cacheValue is not None:
            alreadyAdded = False
            for sizeModelCurrent in cacheValue:
                if json.dumps(sizeModelCurrent) == json.dumps(currentRow):
                    alreadyAdded = True
            if not alreadyAdded:
                cacheValue.append(currentRow)
        else:
            sizeKeyArray = []
            sizeKeyArray.append(currentRow)
            sizeModelCache[cacheKey] = sizeKeyArray
    print("--- Took %s seconds to load Size Model cache. ---" % (time.time() - sz_mapp_start_time))
    return sizeModelCache

#Function to check if element is JSON array
def isJsonArray(element):
    return isinstance(element, list);

#Function to convert json object to json array if it's not otherwise it will just return it
def jsonObjectToArray(element):
    jsonArray = []
    if not isJsonArray(element):
        jsonArray.append(element)
    else:
        jsonArray = element
    return jsonArray

def get_product_sfcs(tags_json, size_model, sizecd_skus_pairs, tags_cache, size_model_cache):
    if size_model == None or tags_json== None or sizecd_skus_pairs == None or len(sizecd_skus_pairs) == 0:
        return
    valid_sfcs = []

    #Make Tags Json object into array since service sometime returns obj and sometimes array
    department_tags = jsonObjectToArray(tags_json['departmentTag'])
    product_type_tags = jsonObjectToArray(tags_json['productTag'])
    category_group_tags = jsonObjectToArray(tags_json['categoryTag'])

    #Filter available SFCs from the first cache by product tags
    for department_tag in department_tags:
        for product_type_tag in product_type_tags:
            for category_group_tag in category_group_tags:
                tags_key = buildSFCsCacheTagKey(department_tag, product_type_tag, category_group_tag)
                tag_valid_sfcs = tags_cache.get(tags_key)
                valid_sfcs = (valid_sfcs or []) + (tag_valid_sfcs or [])

    if valid_sfcs and len(valid_sfcs) == 0:
        return

    valid_sfcs_map = {}
    for sfc in valid_sfcs or []:
        valid_sfcs_map[sfc] = sfc

    size_models = size_model_cache[size_model]
    skus_size_dimension_pair = {}

    # Flag handled skus so you don't process them again, this will ensure that picking first SFC in the list
    # of SFCs per dimension with same sort order in the sheet.
    handled_size_models = {}

    for size_model in size_models:
        current_size_code = size_model['sizeCode']
        current_sfc_id = size_model['sfcId']
        current_dimension = size_model['dimension']
        current_sfc_name = size_model['sizeFacetName']

        for sizecd_sku_pair in sizecd_skus_pairs:
            if sizecd_sku_pair.get(current_size_code) and valid_sfcs_map.get(current_sfc_id):
                sku_dimension_bread_crumb = sizecd_sku_pair.get(current_size_code) + '|' + current_sfc_name + '|' + size_model['sizeFacetBreadCrumb'] + '|Dim_' + current_dimension
                sku_size_dim_pair = []
                if skus_size_dimension_pair.get(sizecd_sku_pair.get(current_size_code)) is not None:
                    sku_size_dim_pair = skus_size_dimension_pair.get(sizecd_sku_pair.get(current_size_code))
                sku_size_dim_pair.append(sku_dimension_bread_crumb)
                skus_size_dimension_pair[str(sizecd_sku_pair.get(current_size_code))] = sku_size_dim_pair
                handled_size_models[sizecd_sku_pair.get(current_size_code) + '_' + current_dimension] = True
    results = []


    for i in skus_size_dimension_pair:
        if len(skus_size_dimension_pair[i]) > 2:
            results.append(skus_size_dimension_pair[i])
    return results


style_tags_index = 19
size_model_index = 30
sku_inventory_status_index=3

#Function that will map the records
def create_style_skus_mapping_records(style_records, output_file, error_output_file, tags_Sfc_cache, sfcs_size_model_cache):
    product_tags = {}
    size_model = ''
    sku_records = []
    at_least_one_sku_instock = False
    for record in style_records:
        attributes = record.split('|')
        if attributes[0] == 'ST':
            product_tags = json.loads(attributes[style_tags_index])
        elif attributes[0] == 'SC':
            size_model = attributes[size_model_index]
        elif attributes[0] == 'SK':# and attributes[sku_inventory_status_index] == '0':
            sku_bus_id_sz_code_pair = {}
            sku_bus_id = attributes[1]
            sizecode = attributes[1][-4:]
            sku_bus_id_sz_code_pair[sizecode] = sku_bus_id
            sku_records.append(sku_bus_id_sz_code_pair)
            at_least_one_sku_instock = True
    SFCs = []
    if at_least_one_sku_instock:
        SFCs = get_product_sfcs(product_tags, size_model, sku_records, tags_Sfc_cache, sfcs_size_model_cache)
        if SFCs is not None and len(SFCs) > 0:
            for sizeFacet in SFCs:
                #Write the facets to the file
                sku = sizeFacet[0][0:13];
                output_file.write(sku + '\t'+ '\t,\t'.join(str(p[13:]) for p in sizeFacet) + '\n')
        else:
            for record in style_records:
                if record.startswith('ST'):
                    attributes = record.split('|')
                    error_output_file.write('{0}|{1}|{2}\n'.format(attributes[0], attributes[1], attributes[3]))


#Function that will create the mapping files based on the input file
def create_mapping_file():
    start_time = time.time()
    print '--- Processing input File {0} ---'.format(str(sys.argv[1]))
    tagsCache = loadSizeFacetCache()
    sizeModelCache = loadSizeModelCache()
    productFeedFileName =  str(sys.argv[1])
    styleRecords = {}
    productMappingOutputFileName = productFeedFileName + '_SFCs'
    productMappingErrorOutputFile = productFeedFileName + '_SFCs_Non'


    #Remove both files if they exist
    try:
        os.remove(productMappingOutputFileName)
        os.remove(productMappingErrorOutputFile)
    except OSError:
        pass

    #output files
    outputFile = open(productMappingOutputFileName,'a+')
    errorOutputFile = open(productMappingErrorOutputFile, 'a+')

    #input file
    inputFileReader = open(productFeedFileName, 'r')
    for line in inputFileReader:
        if line.startswith('ST') and styleRecords.get('records') is not None and len(styleRecords.get('records')) > 0:
            try:
                create_style_skus_mapping_records(styleRecords['records'], outputFile, errorOutputFile, tagsCache,
                                              sizeModelCache)
            except Exception, e:
                print 'Exception happened:' + str(type(e)) + str(e)
                pass
            styleRecords['records'] = []
            styleRecords['records'].append(line)
        else:
            if styleRecords.get('records') == None:
                record = []
                record.append(line)
                styleRecords['records'] = record
            else:
                styleRecords['records'].append(line)
    inputFileReader.close()
    outputFile.close()
    errorOutputFile.close()
    print('--- End of file processing ---')
    print("--- Took %s seconds to process input file. ---" % (time.time() - start_time))

create_mapping_file()




