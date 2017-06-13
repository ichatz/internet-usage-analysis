import csv
import pycountry

# filename - dataset to load
# dataColumn - column of dataset to convert to float
# position - position within the list to place value
def loadDataset(countries, years, filename, dataColumn, position):
    f = open(filename)
    newCountries = 0
    totValues = 0
    for row in csv.reader(f, delimiter=','):
        try:
            key = row[0]
            
            # lookup country
            country = pycountry.countries.lookup(key)             
            
            name = country.name
            year = int(row[1])
            value = float(row[dataColumn])
            
            # exclude very old entries or entries with zero values 
            if (value > 0 and year>=1990):            
                if not (name in countries) :
                    # first encounter of this country
                    newCountries += 1
                    countries[name] = {}          
            
                if not (year in countries[row[0]]):        
                    # first encounter of this year
                    # construct list with missing values for this year
                    countries[name][year] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

                countries[name][year][position] = value

                totValues+=1

                # keep min/max years
                if (year < years['min']):
                    years['min'] = year

                if (year > years['max']):
                    years['max'] = year        

        except (IndexError):
            pass

        except (ValueError):
            pass
            
        except (LookupError):
            pass

    print("Encountered", newCountries, "new countries. Loaded", totValues, "values - Year min", years['min'], "max", years['max'])


def missingEntries(countries, years):
    totMissing = 0
    misValues = {}
    minYear = years['min']
    maxYear = years['max']

    #identify missing years
    for country, data in countries.items():        
        for year in range(minYear, maxYear + 1):
            if not year in data:
                if not country in misValues:
                    misValues[country] = []

                misValues[country].append(year)
                totMissing += 1

    # fill in missing years
    for country, data in misValues.items():        
        for year in data:
            countries[country][year] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    print(totMissing, "missing years in", len(misValues), "countries")


def fillMissing(countries, years):
    totMissing = 0
    totCorrected = 0
    for name, value in countries.items():
        # iterate through 3 datasets
        for dataset in range(0,3):
            prevValue = 0
            year = years['min']
            maxYear = years['max']
            while (year < maxYear):
                value = countries[name][year][dataset]

                if (value == 0 and prevValue == 0):
                    # Value is missing but we are at the start of the series, can't do nothing        
                    pass

                elif (value > 0):
                    prevValue = value

                else :                
                    totMissing += 1

                    # identify next value
                    nextYear = year + 1
                    while (nextYear < maxYear):
                        nextValue = countries[name][nextYear][dataset]

                        if (nextValue > 0):
                            period = nextYear - year + 1                                       
                            increase = (nextValue - prevValue) / period                    

                            # average out missing values
                            for slot in range(year, nextYear):
                                missingValue = prevValue + increase                        
                                countries[name][slot][dataset] = missingValue
                                prevValue = missingValue
                                totCorrected += 1

                            break

                        totMissing += 1
                        nextYear += 1

                year += 1

    print(totMissing, "missing values -", totCorrected, "corrected")
