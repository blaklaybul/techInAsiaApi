import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import networkx as nx
from networkx.readwrite import json_graph

def main(industry,conn, subgraphs):

    nodes = getNodes(industry,conn)
    node_lookup = {
        v["name"]:{
            "name" : v["name"],
            "index" :  i
        }
        for i, v in enumerate(nodes)
    }

    old_links = getLinks(industry,conn)
    links = [ {
    "source": node_lookup[link["source"]]["index"],
    "target": node_lookup[link["target"]]["index"],
    "value": link["value"]
    }
    for link in old_links]

    for_export = {
        "nodes" : nodes,
        "links" : links,
        "meta": {
            "industry" : industry
        }
    }

    dump_it = NetworkAnalysis(for_export, subgraphs)
    return dump_it

def getLinks(industry,conn):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        select
            array_to_json(array_agg(row_to_json(j)))
        from(
            select
                tiacompanyid as target
                ,tiainvestorid as source
                ,count(*) as value
            from fundingstages f
            join investortofundingstage i
                on f.tiafundingstageid = i.tiafundingstageid
            where f.tiacompanyid in (
                select
                    tiacompanyid
                from industries
                where industryname = '"""
                + industry +
                """') group by tiacompanyid, tiainvestorid)j;
        """)
    links = cur.fetchall()[0]["array_to_json"]
    return links



def getNodes(industry,conn):
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            select
                array_to_json(array_agg(row_to_json(j)))
            from(
                select distinct
                    f.tiacompanyid as name
                    , 1 as group
                    , s.country as location
                from fundingstages f
                join investortofundingstage i
                    on f.tiafundingstageid = i.tiafundingstageid
                left join startups s
                    on f.tiacompanyid = s.tiacompanyid
                where f.tiacompanyid in (
                    select
                        tiacompanyid
                    from industries
                    where industryname = '"""
                + industry +
                """')
                UNION ALL
                select distinct
                    i.tiainvestorid as name
                    , 2 as group
                    , ii.investorlocation as location
                from fundingstages f
                join investortofundingstage i
                    on f.tiafundingstageid = i.tiafundingstageid
                left join investors ii
                    on i.tiainvestorid = ii.tiainvestorid
                where f.tiacompanyid in (
                    select
                        tiacompanyid
                    from industries
                    where industryname = '"""
                + industry +
                """')
                )j;
            """)
        nodes = cur.fetchall()[0]["array_to_json"]
        return nodes

def NetworkAnalysis(jsonGraph,subgraphs):
    """gets graph defined by for export json and computes the top 3
    most connected subgraphs"""

    G = json_graph.node_link_graph(jsonGraph)
    graphs = sorted(nx.connected_component_subgraphs(G), key = len, reverse=True)

    tuple(GC + str(i) for i in range(subgraphs)) = graphs[0:subgraphs]
    top5 = nx.compose_all([GC1,GC2,GC3,GC4,GC5])
    deg = top5.degree()
    nx.set_node_attributes(top5, "degree", deg)
    take = {
        "nodes": json_graph.node_link_data(top5)["nodes"],
        "links": json_graph.node_link_data(top5)["links"]
        }
    return take
