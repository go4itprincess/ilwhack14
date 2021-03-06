import json
from flask import Flask, jsonify, request
import _mysql
import os
from os.path import join, getsize
from werkzeug.utils import secure_filename
from db_connect import dbPasswd

app = Flask(__name__)

# DB connection
db = _mysql.connect(host="localhost", user="msp", passwd=dbPasswd, db="msp")
db.query("SET SESSION group_concat_max_len=8192;")


def check_cache(name):
    try:
        with open("/var/www/msp/testapp/static/cache/"+name,"r") as fo:
            return fo.read()
    except IOError:
        return False

@app.route("/")
def hello():
    return app.send_static_file('index.html')

@app.route("/<filename>.css")
def get_css(filename):
    return app.send_static_file(filename + '.css')

@app.route("/<filename>.js")
def get_js(filename):
    return app.send_static_file(filename + '.js')

@app.route("/<filename>.json")
def get_json(filename):
    return app.send_static_file(filename + '.json')

@app.route("/<filename>.ico")
def get_ico(filename):
    return app.send_static_file(filename + '.ico')

@app.route("/<filename>.png")
def get_png(filename):
    return app.send_static_file(filename + '.png')

@app.route("/constituency/<string:constituency>")
def const_info(constituency):
    cache = check_cache("c_"+secure_filename(constituency))
    if cache != False:
        return jsonify(json.loads(cache))

    db.query("""
        SELECT
            m.name,
            m.surname,
            m.party,
            m.url,
            (AVG(s_gen.2006*1+s_gen.2009*2+s_gen.2012*7)/6505*10-18)/67*100 AS rank_gen,
            m.total_interventions,
            m.avg_intervention_len,
            m.total_mentions_of_constituency,
            m.interventions_with_mention,
            m.mentions_percentage_of_total_text,
            m.percentage_of_interventions_with_mention,
            m.id,
            GROUP_CONCAT(DISTINCT CONCAT("[\\\"", w.word, "\\\",", w.weight, "]") SEPARATOR ', '),
            (AVG(s_cri.2006*1+s_cri.2009*2+s_cri.2012*7)/6505*10-24)/52*100 AS rank_cri,
            (AVG(s_edu.2006*1+s_edu.2009*2+s_edu.2012*7)/6505*10-18)/74*100 AS rank_edu,
            (AVG(s_emp.2006*1+s_emp.2009*2+s_emp.2012*7)/6505*10-19)/65*100 AS rank_emp,
            (AVG(s_geo.2006*1+s_geo.2009*2+s_geo.2012*7)/6505*10-11)/77*100 AS rank_geo,
            (AVG(s_hea.2006*1+s_hea.2009*2+s_hea.2012*7)/6505*10-17)/63*100 AS rank_hea,
            (AVG(s_hou.2006*1+s_hou.2009*2+s_hou.2012*7)/6505*10-9)/67*100 AS rank_hou,
            (AVG(s_inc.2006*1+s_inc.2009*2+s_inc.2012*7)/6505*10-18)/62*100 AS rank_inc,
            c.population,
            c.name,
            c.council,
            c.region
        FROM constituencies c
        LEFT JOIN MSPs m ON c.name=m.constituency
        LEFT JOIN datazones d ON c.id = d.constituency
        LEFT JOIN MSP_words w ON w.MSP_id = m.id
        LEFT JOIN simd_general s_gen on s_gen.datazone = d.code
        LEFT JOIN simd_crime s_cri on s_cri.datazone = d.code
        LEFT JOIN simd_education s_edu on s_edu.datazone = d.code
        LEFT JOIN simd_employment s_emp on s_emp.datazone = d.code
        LEFT JOIN simd_geoacc s_geo on s_geo.datazone = d.code
        LEFT JOIN simd_health s_hea on s_hea.datazone = d.code
        LEFT JOIN simd_housing s_hou on s_hou.datazone = d.code
        LEFT JOIN simd_income s_inc on s_inc.datazone = d.code
        WHERE c.name="{constituency}"
        GROUP BY c.id
    """.format(constituency=constituency))
    r = db.use_result()
    row = r.fetch_row()
    result = []

    while row:
        row = row[0]
        msp = {
            'MSP_id': row[11],
            'name': row[0],
            'surname': row[1],
            'party': row[2],
            'url': row[3],
            'rank_gen': row[4],
            'total_interventions': row[5],
            'avg_intervention_len': row[6],
            'total_mentions_of_constituency': row[7],
            'interventions_with_mention': row[8],
            'mentions_percentage_of_total_text': row[9],
            'percentage_of_interventions_with_mention': row[10],
            'words': "[{0}]".format(row[12]),
            'rank_cri': row[13],
            'rank_edu': row[14],
            'rank_emp': row[15],
            'rank_geo': row[16],
            'rank_hea': row[17],
            'rank_hou': row[18],
            'rank_inc': row[19],
            'population': row[20],
            'constituency': row[21],
            'council': row[22],
            'region': row[23]
        }

        result += [msp]
        row = r.fetch_row()

    result = {'result': result}

    with open("/var/www/msp/testapp/static/cache/c_"+secure_filename(constituency),"w") as fo:
        fo.write(json.dumps(result))

    return jsonify(result)

@app.route("/region/<string:constituency>")
def region_info(constituency):
    cache = check_cache("r_"+secure_filename(constituency))
    if cache != False:
        return jsonify(json.loads(cache))

    db.query("""
        SELECT
            m.name,
            m.surname,
            m.party,
            m.url,
            (AVG(s_gen.2006*1+s_gen.2009*2+s_gen.2012*7)/6505*10-18)/67*100 AS rank_gen,
            m.total_interventions,
            m.avg_intervention_len,
            m.total_mentions_of_constituency,
            m.interventions_with_mention,
            m.mentions_percentage_of_total_text,
            m.percentage_of_interventions_with_mention,
            m.id,
            GROUP_CONCAT(DISTINCT CONCAT("[\\\"", w.word, "\\\",", w.weight, "]") SEPARATOR ', '),
            c.name,
            c.council,
            c.region,
            c.population
        FROM constituencies c
        LEFT JOIN MSPs m ON c.region=m.constituency
        LEFT JOIN MSP_words w ON w.MSP_id = m.id
        LEFT JOIN constituencies c2 ON c.id = c2.id
        LEFT JOIN datazones d ON c2.id = d.constituency
        LEFT JOIN simd_general s_gen on s_gen.datazone = d.code
        WHERE c.name="{constituency}"
        GROUP BY m.id
    """.format(constituency=constituency))
    r = db.use_result()
    row = r.fetch_row()
    result = []

    while row:
        row = row[0]
        msp = {
            'MSP_id': row[11],
            'name': row[0],
            'surname': row[1],
            'party': row[2],
            'url': row[3],
            'rank_gen': row[4],
            'total_interventions': row[5],
            'avg_intervention_len': row[6],
            'total_mentions_of_constituency': row[7],
            'interventions_with_mention': row[8],
            'mentions_percentage_of_total_text': row[9],
            'percentage_of_interventions_with_mention': row[10],
            'words': "[{0}]".format(row[12]),
            'constituency': row[13],
            'council': row[14],
            'region': row[15],
            'population': row[16]
        }

        result += [msp]
        row = r.fetch_row()

    result = {'result':result}

    with open("/var/www/msp/testapp/static/cache/r_"+secure_filename(constituency),"w") as fo:
        fo.write(json.dumps(result))

    return jsonify(result)


@app.route("/stats/", methods=['POST', 'GET'])
def get_stats():

    cache = check_cache("stats")
    if cache != False:
        return jsonify(json.loads(cache))

    categories = request.form.getlist('categories[]')
    fields = {'c_id':'c.id', 'c_name':'c.name', 'c_council':'c.council', 'c_region':'c.region', 'c_population':'c.population'}

    if ("rank_gen" in categories) or (len(categories)==0):
        fields['rank_gen']="(AVG(s_gen.2006*1+s_gen.2009*2+s_gen.2012*7)/6505*10-18)/67*100 AS rank_gen"
        
    if ("rank_cri" in categories) or (len(categories)==0):
        fields['rank_cri']="(AVG(s_cri.2006*1+s_cri.2009*2+s_cri.2012*7)/6505*10-24)/52*100 AS rank_cri"
        
    if ("rank_edu" in categories) or (len(categories)==0):
        fields['rank_edu']="(AVG(s_edu.2006*1+s_edu.2009*2+s_edu.2012*7)/6505*10-18)/74*100 AS rank_edu"
        
    if ("rank_emp" in categories) or (len(categories)==0):
        fields['rank_emp']="(AVG(s_emp.2006*1+s_emp.2009*2+s_emp.2012*7)/6505*10-19)/65*100 AS rank_emp"
        
    if ("rank_geo" in categories) or (len(categories)==0):
        fields['rank_geo']="(AVG(s_geo.2006*1+s_geo.2009*2+s_geo.2012*7)/6505*10-11)/77*100 AS rank_geo"
        
    if ("rank_gen" in categories) or (len(categories)==0):
        fields['rank_hea']="(AVG(s_hea.2006*1+s_hea.2009*2+s_hea.2012*7)/6505*10-17)/63*100 AS rank_hea"
        
    if ("rank_hou" in categories) or (len(categories)==0):
        fields['rank_hou']="(AVG(s_hou.2006*1+s_hou.2009*2+s_hou.2012*7)/6505*10-9)/67*100 AS rank_hou"
        
    if ("rank_inc" in categories) or (len(categories)==0):
        fields['rank_inc']="(AVG(s_inc.2006*1+s_inc.2009*2+s_inc.2012*7)/6505*10-18)/62*100 AS rank_inc"

    if ("total_interventions" in categories) or (len(categories)==0):
        fields['total_interventions']="AVG(m.total_interventions)"

    if ("avg_intervention_len" in categories) or (len(categories)==0):
        fields['avg_intervention_len']="AVG(m.avg_intervention_len)"

    if ("total_mentions_of_constituency" in categories) or (len(categories)==0):
        fields['total_mentions_of_constituency']="AVG(m.total_mentions_of_constituency)"

    if ("interventions_with_mention" in categories) or (len(categories)==0):
        fields['interventions_with_mention']="AVG(m.interventions_with_mention)"

    if ("mentions_percentage_of_total_text" in categories) or (len(categories)==0):
        fields['mentions_percentage_of_total_text']="AVG(m.mentions_percentage_of_total_text)"

    if ("percentage_of_interventions_with_mention" in categories) or (len(categories)==0):
        fields['percentage_of_interventions_with_mention']="AVG(m.percentage_of_interventions_with_mention)"

    db.query("""
        SELECT
            {fields}
        FROM constituencies c
        LEFT JOIN MSPs m ON c.name=m.constituency
        LEFT JOIN datazones d ON c.id = d.constituency
        LEFT JOIN simd_general s_gen on s_gen.datazone = d.code
        LEFT JOIN simd_crime s_cri on s_cri.datazone = d.code
        LEFT JOIN simd_education s_edu on s_edu.datazone = d.code
        LEFT JOIN simd_employment s_emp on s_emp.datazone = d.code
        LEFT JOIN simd_geoacc s_geo on s_geo.datazone = d.code
        LEFT JOIN simd_health s_hea on s_hea.datazone = d.code
        LEFT JOIN simd_housing s_hou on s_hou.datazone = d.code
        LEFT JOIN simd_income s_inc on s_inc.datazone = d.code
        GROUP BY c.id
    """.format(fields=' , '.join(fields.values())))

    r = db.use_result()
    result = []
    row = r.fetch_row()

    while row:
        row = row[0]
        constituency = {}
        for (i, field) in enumerate(fields.keys()):
            constituency[field] = row[i]

        result += [constituency]
        row = r.fetch_row()

    result = {'result':result}

    with open("/var/www/msp/testapp/static/cache/stats","w") as fo:
        fo.write(json.dumps(result))

    return jsonify(result)


if __name__ == "__main__":
    app.run()
