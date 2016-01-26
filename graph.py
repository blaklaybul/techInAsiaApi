from __future__ import division
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import networkx as nx
from networkx.readwrite import json_graph

def main(industry,conn,subgraphs):

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
                    , s.companyname as coName
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
                    , ii.investorname as coName
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
    nodes = [len(graph.nodes()) for graph in graphs]
    subgraphs_nodes = [len(graph.nodes()) for graph in graphs[0:subgraphs]]
    print nodes
    print subgraphs_nodes
    frac = sum(subgraphs_nodes)/sum(nodes)
    print subgraphs, "represents", frac*100, "% of nodes"
    topn = nx.compose_all(graphs[0:subgraphs])
    deg = topn.degree()
    cent_deg = nx.degree_centrality(topn)
    nx.set_node_attributes(topn, "degree", deg)
    nx.set_node_attributes(topn, "cent_deg", cent_deg)
    take = {
        "nodes": json_graph.node_link_data(topn)["nodes"],
        "links": json_graph.node_link_data(topn)["links"],
        "frac" : frac
        }
    return take
