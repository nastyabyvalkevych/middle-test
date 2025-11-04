"""
Є граф, який серіалізовано у форматі ttl (файл з іменем countrues_info.ttl).
В графі наведено інформацію по країнам світу.
Візуальне представлення графу для країни United Kingdom надано у файлі (rdf-grapher.png).
Написати Python-скрипт, який на базі заданого графу повертає загальну чисельність населення кожного континенту.
"""

from rdflib import Graph, Namespace, RDF
from collections import defaultdict


def load_graph(ttl_file):
    print(f"Loading... {ttl_file}")
    g = Graph()
    g.parse(ttl_file, format='turtle')
    print(f"Кількість триплетів: {len(g)}")
    return g


def calculate_population_by_continent(graph):
    NS = Namespace("http://example.com/demo/")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

    continent_population = defaultdict(int)

    continent_names = {}

    print("\nLoading...")

    for continent in graph.subjects(RDF.type, NS.Continent):
        for label in graph.objects(continent, SKOS.prefLabel):
            continent_names[str(continent)] = str(label)

    print(f"Continents: {len(continent_names)}")

    processed_countries = 0
    for country in graph.subjects(RDF.type, NS.Country):
        continent = None
        for cont in graph.objects(country, NS.part_of_continent):
            continent = str(cont)
            break

        population = None
        for pop in graph.objects(country, NS.population):
            population = int(pop)
            break

        if continent and population:
            continent_population[continent] += population
            processed_countries += 1

    print(f"Processed countries: {processed_countries}")

    result = {}
    for continent_uri, population in continent_population.items():
        continent_name = continent_names.get(continent_uri, continent_uri)
        result[continent_name] = population

    return result


def display_results(population_data):
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)

    sorted_data = sorted(population_data.items(), key=lambda x: x[1], reverse=True)

    total_population = 0
    for continent, population in sorted_data:
        formatted_pop = f"{population:,}".replace(",", " ")
        print(f"{continent:20} | {formatted_pop:>15} осіб")
        total_population += population

    print("-" * 60)
    formatted_total = f"{total_population:,}".replace(",", " ")
    print(f"{'total number of persons':20} | {formatted_total:>15}")
    print("=" * 60)


def main():
    try:
        ttl_file = "./countrues_info.ttl"
        graph = load_graph(ttl_file)
        population_data = calculate_population_by_continent(graph)
        display_results(population_data)

    except FileNotFoundError:
        print(f"error {ttl_file} not found")
    except Exception as e:
        print(f"error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()