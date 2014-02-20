from flask import Flask, jsonify, request
import _mysql

app = Flask(__name__)

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

@app.route("/constituency/<string:constituency>")
def const_info(constituency):
    db = _mysql.connect(host="localhost", user="ilwhack14", passwd="hackathon", db="ilwhack14")
    db.query("""
        SELECT
            m.name,
            m.surname,
            m.party,
            m.url,
            AVG(s_gen.2006*1+s_gen.2009*2+s_gen.2012*7)/6505*10 AS rank_gen,
            m.total_interventions,
            m.avg_intervention_len,
            m.total_mentions_of_constituency,
            m.interventions_with_mention,
            m.mentions_percentage_of_total_text,
            m.percentage_of_interventions_with_mention,
            m.id,
            GROUP_CONCAT(DISTINCT CONCAT("[\\\"", w.word, "\\\",", w.weight, "]") SEPARATOR ', ')
            AVG(s_cri.2006*1+s_cri.2009*2+s_cri.2012*7)/6505*10 AS rank_cri,
            AVG(s_ed.2006*1+s_ed.2009*2+s_ed.2012*7)/6505*10 AS rank_ed,
            AVG(s_emp.2006*1+s_emp.2009*2+s_emp.2012*7)/6505*10 AS rank_emp,
            AVG(s_geo.2006*1+s_geo.2009*2+s_geo.2012*7)/6505*10 AS rank_geo,
            AVG(s_hea.2006*1+s_hea.2009*2+s_hea.2012*7)/6505*10 AS rank_hea,
            AVG(s_hou.2006*1+s_hou.2009*2+s_hou.2012*7)/6505*10 AS rank_hou,
            AVG(s_inc.2006*1+s_inc.2009*2+s_inc.2012*7)/6505*10 AS rank_inc
        FROM constituencies c
        LEFT JOIN MSPs m ON c.name=m.constituency
        LEFT JOIN datazones d ON c.id = d.constituency
        LEFT JOIN MSP_words w ON w.MSP_id = m.id
        LEFT JOIN simd_general s_gen on s_gen.datazone = d.code
        LEFT JOIN simd_crime s_cri on s_cri.datazone = d.code
        LEFT JOIN simd_education s_ed on s_ed.datazone = d.code
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
    msp = {
        'MSP_id': row[0][11],
        'name': row[0][0],
        'surname': row[0][1],
        'party': row[0][2],
        'url': row[0][3],
        'rank_gen': row[0][4],
        'total_interventions': row[0][5],
        'avg_intervention_len': row[0][6],
        'total_mentions_of_constituency': row[0][7],
        'interventions_with_mention' : row[0][8],
        'mentions_percentage_of_total_text': row[0][9],
        'percentage_of_interventions_with_mention': row[0][10],
        'words': "[{0}]".format(row[0][12]),
        'rank_cri': row[0][13],
        'rank_ed': row[0][13],
        'rank_emp': row[0][17],
        'rank_geo': row[0][14],
        'rank_hea': row[0][15],
        'rank_hou': row[0][16],
        'rank_inc': row[0][18]
    }
    while row:
        result += [msp]
        row = r.fetch_row()
    result = {'result':result}
    return jsonify(result)


@app.route("/stats/", methods=['POST', 'GET'])
def get_stats():
    print(request.form.getlist('categories[]'))
    categories = request.form.getlist('categories[]')
    fields = {'c_id':'c.id', 'c_name':'c.name'}

    if ("rank" in categories) or (len(categories)==0):
        fields['rank']="AVG(simd.2006*1+simd.2009*2+simd.2012*7)/6505*10 AS rank"

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

    db = _mysql.connect(host="localhost", user="ilwhack14", passwd="hackathon", db="ilwhack14")
    db.query("""
        SELECT
            {fields}
        FROM constituencies c
        LEFT JOIN MSPs m ON c.name=m.constituency
        LEFT JOIN datazones d ON c.id = d.constituency
        LEFT JOIN simd_general simd on simd.datazone = d.code
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
    return jsonify(result)


if __name__ == "__main__":
    app.run()
