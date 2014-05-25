#-*- coding: utf8 -*-
from flask import Flask, render_template, make_response, session, redirect, url_for, escape, request,jsonify,Response   
import datetime
from dateutil import parser
import time as T, networkx as x, json # json.dumps
import requests
import MySQLdb, cPickle, numpy as n

app = Flask(__name__)

# 34 é o ID das OSCs
try:
    f=open("pickleDir/proponentes.cpicke","rb")
    proponentes=cPickle.load(f)
    f.close()
    print "proponentes carregados"
except:
    url="http://api.convenios.gov.br/siconv/v1/consulta/proponentes.json?id_natureza_juridica=34"
    r=requests.get(url)
    proponentes=json.loads(r.content)['proponentes']
    f=open("pickleDir/proponentes.cpicke","wb")
    cPickle.dump(proponentes,f)
    f.close()
    print "proponentes feitos"

try:
    f=open("pickleDir/convenios_proponente.cpicke","rb")
    convenios_proponente=cPickle.load(f)
    f.close()
    print "convenios_proponente carregado"
except:
    print "fazendo convenio de cada proponente"
    convenios_proponente=[]
    IDS=[]
    for prop in proponentes:
        #url=prop["convenios"]
        url_="http://api.convenios.gov.br/siconv/v1/consulta/convenios.json?id_proponente="+str(prop["id"])
        r=requests.get(url_)
        convenios= json.loads(r.content)['convenios']
        print convenios
        convenios_proponente.append(convenios)
    f=open("pickleDir/convenios_proponente.cpicke","wb")
    cPickle.dump(convenios_proponente,f)
    f.close()
    print "feito convenio de cada proponente"
if len(convenios_proponente) < len(proponentes):
    for prop in proponentes[len(convenios_proponente):]:
        url_="http://api.convenios.gov.br/siconv/v1/consulta/convenios.json?id_proponente="+str(prop["id"])
        r=requests.get(url_)
        convenios= json.loads(r.content)['convenios']
        convenios_proponente.append(convenios)
        


IDs=[]
for convs in convenios_proponente:
    for conv in convs:
        oID=conv["orgao_concedente"]["Orgao"]["id"]
        print oID
        if oID in IDs:
            print "id jah existe"
        IDs.append(oID)
try:
    f=open("pickleDir/habilitacoes_proponente.cpicke","rb")
    habilitacoes_proponente=cPickle.load(f)
    f.close()
    print "habilitacoes_proponente carregado"
except:
    print "fazendo habilitacoes de cada proponente"
    habilitacoes_proponente=[]
    IDS=[]
    for prop in proponentes:
        url_="http://api.convenios.gov.br/siconv/v1/consulta/habilitacoes_area_atuacao.json?id_proponente="+str(prop["id"])
        r=requests.get(url_)
        habilitacoes= json.loads(r.content)['habilitacoes_area_atuacao']
        print habilitacoes
        habilitacoes_proponente.append(habilitacoes)
    f=open("pickleDir/habilitacoes_proponente.cpicke","wb")
    cPickle.dump(habilitacoes_proponente,f)
    f.close()
    print "feito habilitacoes de cada proponente"
IDs_=[]
for habs in habilitacoes_proponente:
    for hab in habs:
        #oID=hab["id"]
        oID=hab["subarea"]["SubAreaAtuacaoProponente"]["id"]
        print oID
        if oID in IDs_:
            print "HAB id jah existe"
        IDs_.append(oID)
############
# fazer as duas redes:
# 1) cada prop eh um vertice
# 2) caso eles tenham a mesma org concedente há aresta
# 3) caso eles tenham a mesma subarea de habilitacao há aresta

# procedimento
# 1) cada vertice tem a "id" de um proponente (ou o "cnpj")
# e label "nome"
# pegar "nome_responsavel" e "telefone" e "cep" "endereco"
# talvez jah pegar tb areas de habilitacao 
# e tb orgao conveniado

g2=x.MultiGraph()
g=x.Graph()
g3=x.Graph()

i=0
for prop in proponentes:
    #g.add_node(prop["id"],tdata=prop,conv=convenios_proponente[i],hab=habilitacoes_proponente[i]) #otimizar tdata
    g.add_node(prop["id"],tdata=prop,conv=convenios_proponente[i],hab=habilitacoes_proponente[i]) #otimizar tdata
    g2.add_node(prop["id"],tdata=prop,conv=convenios_proponente[i],hab=habilitacoes_proponente[i]) #otimizar tdata
    g3.add_node(prop["id"],tdata=prop,conv=convenios_proponente[i],hab=habilitacoes_proponente[i]) #otimizar tdata
    i+=1

i=0
for conv in convenios_proponente:
    IDS0=[]
    for conv_ in conv:
        IDS0.append(conv_["orgao_concedente"]["Orgao"]["id"])
    j=0
    for conv2 in convenios_proponente[i+1:]:
        peso=0
        for conv2_ in conv2:
            oid=conv2_["orgao_concedente"]["Orgao"]["id"]
            if oid in IDS0:
                peso+=1
                # tem aresta
        if peso>0:
            id_prop1=proponentes[i]["id"]
            id_prop2=proponentes[j]["id"]
            g.add_edge(id_prop1,id_prop2,weight=peso)
            g2.add_edge(id_prop1,id_prop2,0,weight=peso)
            #g2.add_edge(id_prop1,id_prop2,1,weight=peso)
        j+=1
    i+=1
gg=g
i=0
for hab in habilitacoes_proponente:
    IDS0=[]
    for hab_ in hab:
        IDS0.append(hab_["subarea"]["SubAreaAtuacaoProponente"]["id"])
    j=0
    for hab2 in habilitacoes_proponente[i+1:]:
        peso=0
        for hab2_ in hab2:
            oid=hab2_["subarea"]["SubAreaAtuacaoProponente"]["id"]
            if oid in IDS0:
                peso+=1
                # tem aresta
        if peso>0:
            id_prop1=proponentes[i]["id"]
            id_prop2=proponentes[j]["id"]
            g3.add_edge(id_prop1,id_prop2,weight=peso)
            g2.add_edge(id_prop1,id_prop2,1,weight=peso)
        j+=1
    i+=1
gg2=g2
gg3=g3

@app.route("/redeOSCs/")
def rO():
    graus=gg.degree()
    clustering=x.clustering(gg)
    nodes=gg.nodes(data=True)
    nodes_=[]
    for node in nodes:
        #print node[1]
        nodes_+=[{"name":node[1]["tdata"]["nome"],"group":1,"degree":graus[node[0]],"clustering":clustering[node[0]]}]
    edges=gg.edges(data=True)
    edges_=[]
    nodes=gg.nodes()
    for ee in edges:
        print ee
        edges_+=[{"source":nodes.index(ee[0]),"target":nodes.index(ee[1]),"value":ee[2]["weight"]}]
    return jsonify(nodes=nodes_,links=edges_)

@app.route("/redeOSCs3/")
def rO3():
    graus=gg3.degree()
    clustering=x.clustering(gg3)
    nodes=gg3.nodes(data=True)
    nodes_=[]
    for node in nodes:
        #print node[1]
        nodes_+=[{"name":node[1]["tdata"]["nome"],"group":1,"degree":graus[node[0]],"clustering":clustering[node[0]]}]
    edges=gg3.edges(data=True)
    edges_=[]
    nodes=gg3.nodes()
    for ee in edges:
        print ee
        edges_+=[{"source":nodes.index(ee[0]),"target":nodes.index(ee[1]),"value":ee[2]["weight"]}]
    return jsonify(nodes=nodes_,links=edges_)


@app.route("/redeOSCs2/")
def rO2():
    graus=gg2.degree()
    nodes=gg2.nodes(data=True)
    nodes_=[]
    for node in nodes:
        #print node[1]
        nodes_+=[{"name":node[1]["tdata"]["nome"],"group":1,"degree":graus[node[0]]}]
    edges=gg2.edges(data=True,keys=True)
    edges_=[]
    edges2_=[]
    nodes=gg2.nodes()
    for ee in edges:
        if ee[2]==0:
            edges_+=[{"source":nodes.index(ee[0]),"target":nodes.index(ee[1]),"value":ee[3]["weight"]}]
        else:
            edges2_+=[{"source":nodes.index(ee[0]),"target":nodes.index(ee[1]),"value":ee[3]["weight"]}]
    return jsonify(nodes=nodes_,links=edges_,links2=edges2_)



@app.route("/redeTeste/")
def rT():
    g=x.erdos_renyi_graph(20,0.3)
    graus=g.degree()
    clustering=x.clustering(g)
    nodes=g.nodes()
    nodes_=[]
    for node in nodes:
        nodes_+=[{"name":node,"group":1,"degree":graus[node],"clustering":clustering[node]}]
    edges=g.edges()
    edges_=[]
    for ee in edges:
        print ee
        edges_+=[{"source":nodes.index(ee[0]),"target":nodes.index(ee[1]),"value":1}]
    return jsonify(nodes=nodes_,links=edges_)

@app.route("/")
def hello_world():
    return "oi ro!"


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
