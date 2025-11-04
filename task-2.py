"""
Використовуючи відкритий SPARQL endpoint http://dbpedia.org/sparql,
напишіть SPARQL запит для визначення назви найбільшої за площею області України.
"""

from SPARQLWrapper import SPARQLWrapper, JSON


def get_largest_ukraine_region():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?name ?area
    WHERE {
        ?oblast a dbo:Place ;
                rdfs:label ?name ;
                dbo:country dbr:Ukraine .

        {
            ?oblast dbo:areaTotal ?area .
        }
        UNION
        {
            ?oblast dbo:areaKm ?area .
        }

        FILTER(CONTAINS(STR(?oblast), "Oblast"))

        FILTER(LANG(?name) = "uk")

        FILTER(DATATYPE(?area) = <http://www.w3.org/2001/XMLSchema#double>)
    }
    ORDER BY DESC(?area)
    LIMIT 1
    """

    print("query to DBpedia...")

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()

        print("Results:")

        if results["results"]["bindings"]:
            for result in results["results"]["bindings"]:
                name = result["name"]["value"] if "name" in result else "Undefined"
                area = result["area"]["value"] if "area" in result else "Undefined"

                try:
                    area_float = float(area)
                    if area_float > 1000000:
                        area_km2 = area_float / 1000000
                        area_formatted = f"{area_km2:,.2f} км²"
                    else:
                        area_formatted = f"{area_float:,.2f} км²"
                except:
                    area_formatted = f"{area} (одиниці невідомі)"

                print(f"\nНайбільша область України:")
                print(f"   Назва: {name}")
                print(f"   Площа: {area_formatted}")
        else:
            print("No results found.")

        return results

    except Exception as e:
        print(f"error: {e}")
        return None


def main():
    get_largest_ukraine_region()

if __name__ == "__main__":
    main()