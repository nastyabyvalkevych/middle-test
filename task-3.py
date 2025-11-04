"""
Використовуючи бібліотеки RdfLib, SPARQLWrapper та відкритий endpoint
написати Python-скрипт, який буде повертати кріїни, в яких розмовляють англійською.
Країни необхідно впорядкувати за площею.
"""

from rdflib import Graph, Namespace
from SPARQLWrapper import SPARQLWrapper, JSON


def load_graph(ttl_file):
    print(f"Loading... {ttl_file}")
    g = Graph()
    g.parse(ttl_file, format='turtle')
    print(f"Кількість триплетів: {len(g)}")
    return g


def find_english_speaking_countries_sparql(graph):
    query = """
    PREFIX : <http://example.com/demo/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT ?country ?countryName ?area ?population
    WHERE {
        ?country a :Country ;
                 :country_name ?countryName ;
                 :area_in_sq_km ?area .

        OPTIONAL {
            ?country :population ?population .
        }

        ?countryLang :spoken_in ?country ;
                     :language_value <http://example.com/demo/Language/eng> .

        FILTER(?area > 0)
    }
    ORDER BY DESC(?area)
    """


    results = graph.query(query)

    countries = []
    for row in results:
        country_data = {
            'name': str(row.countryName),
            'area': float(row.area),
            'population': int(row.population) if row.population else 0,
            'uri': str(row.country)
        }
        countries.append(country_data)

    print("Results SPARQL:")
    print(f"English-speaking countries: {len(countries)}")
    return countries

def find_english_speaking_countries_rdflib(graph):

    print("\nRDFLib API...")

    NS = Namespace("http://example.com/demo/")

    english_lang_uri = NS["Language/eng"]

    countries_data = {}

    print("\nEnglish-speaking countries...")
    for country_lang in graph.subjects(NS.language_value, english_lang_uri):
        for country in graph.objects(country_lang, NS.spoken_in):
            if str(country) not in countries_data:
                countries_data[str(country)] = {'uri': str(country)}

    print(f"Found: {len(countries_data)}")

    print("\nАdditional information about countries...")
    countries = []

    for country_uri in countries_data:
        country_node = NS[country_uri.split('/')[-1]]

        name = None
        for n in graph.objects(country_node, NS.country_name):
            name = str(n)
            break

        area = None
        for a in graph.objects(country_node, NS.area_in_sq_km):
            area = float(a)
            break

        population = None
        for p in graph.objects(country_node, NS.population):
            population = int(p)
            break

        if name and area and area > 0:
            countries.append({
                'name': name,
                'area': area,
                'population': population if population else 0,
                'uri': country_uri
            })

    countries.sort(key=lambda x: x['area'], reverse=True)

    print(f"All: {len(countries)}")

    return countries


def display_results(countries):

    print("=" * 80)
    print("Results RdfLib:")
    print(f"{'№':<4} {'Країна':<35} {'Площа (км²)':<18} {'Населення':<15}")
    print("-" * 80)

    for i, country in enumerate(countries, 1):
        area_formatted = f"{country['area']:,.0f}".replace(",", " ")
        pop_formatted = f"{country['population']:,}".replace(",", " ") if country['population'] else "Дані відсутні"

        print(f"{i:<4} {country['name']:<35} {area_formatted:>18} {pop_formatted:>15}")


def query_dbpedia_for_comparison():

    print("\n" + "=" * 80)
    print("Results DBpedia:")
    print("=" * 80)

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?name ?area
        WHERE {
            ?country a dbo:Country ;
                     rdfs:label ?name .

            {
                ?country dbo:officialLanguage dbr:English_language .
            }
            UNION
            {
                ?country dbp:officialLanguages ?lang .
                FILTER(CONTAINS(STR(?lang), "English") || CONTAINS(STR(?lang), "english"))
            }

            {
                ?country dbo:areaTotal ?area .
            }
            UNION
            {
                ?country dbp:areaSqKm ?area .
            }
            UNION
            {
                ?country dbp:areaKm ?area .
            }

            FILTER(LANG(?name) = "en")

            FILTER(isNumeric(?area))
            FILTER(?area > 0)
        }
        ORDER BY DESC(?area)
        LIMIT 25
        """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(30)

    try:
        results = sparql.query().convert()

        if results["results"]["bindings"]:

            for i, result in enumerate(results["results"]["bindings"], 1):
                name = result.get("name", {}).get("value", "Невідомо")
                area = result.get("area", {}).get("value", None)

                if area:
                    try:
                        area_float = float(area)
                        if area_float > 1000000:
                            area_km2 = area_float / 1000000
                            area_formatted = f"{area_km2:,.0f} км²"
                        else:
                            area_formatted = f"{area_float:,.0f} км²"
                    except ValueError:
                        area_formatted = str(area)
                else:
                    area_formatted = "Дані відсутні"

                print(f"{i:<4} {name:<35} {area_formatted:<20}")

            print("-" * 80)
        else:
            print("\nerrror")
    except Exception as e:
        print(f"\n❌ error: {e}")



def main():
    ttl_file = "./countrues_info.ttl"

    try:
        graph = load_graph(ttl_file)

        countries_sparql = find_english_speaking_countries_sparql(graph)

        if countries_sparql:
            display_results(countries_sparql)
        else:
            countries_rdflib = find_english_speaking_countries_rdflib(graph)
            if countries_rdflib:
                display_results(countries_rdflib)
            else:
                print("not found")

        query_dbpedia_for_comparison()

    except Exception as e:
        print(f"error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()