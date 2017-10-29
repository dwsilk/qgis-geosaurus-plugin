# -*- coding: utf-8 -*-

import psycopg2


ONE_GEOM_POSTGIS_FUNCTION_SQL = """
SELECT format('%I(%s)', p.proname, oidvectortypes(p.proargtypes)) 
FROM  pg_proc p
JOIN  pg_namespace ns ON p.pronamespace = ns.oid
WHERE ns.nspname = 'public'
AND   format('%I(%s)', p.proname, oidvectortypes(p.proargtypes)) LIKE '%(geometry)'
AND   format('%I(%s)', p.proname, oidvectortypes(p.proargtypes)) LIKE 'st_%';
"""

TWO_GEOM_POSTGIS_FUNCTION_SQL = """
SELECT replace(format('%I(%s)', p.proname, oidvectortypes(p.proargtypes)), '(geometry, geometry)', '')
FROM   pg_proc p
JOIN   pg_namespace ns ON p.pronamespace = ns.oid
WHERE  ns.nspname = 'public'
AND    format('%I(%s)', p.proname, oidvectortypes(p.proargtypes)) LIKE '%(geometry, geometry)'
AND    format('%I(%s)', p.proname, oidvectortypes(p.proargtypes)) LIKE 'st_%';
"""

POSTGIS_VERSION_SQL = """
SELECT postgis_lib_version();
"""

# Add necessary database connection details here
conn = psycopg2.connect()
conn.autocommit = True


def one_geom_list():
    curs = conn.cursor()
    curs.execute(ONE_GEOM_POSTGIS_FUNCTION_SQL)
    result = curs.fetchall()
    curs.close()
    return result


def two_geom_list():
    curs = conn.cursor()
    curs.execute(TWO_GEOM_POSTGIS_FUNCTION_SQL)
    result = curs.fetchall()
    curs.close()
    return result


def postgis_version():
    curs = conn.cursor()
    curs.execute(POSTGIS_VERSION_SQL)
    result = curs.fetchone()[0]
    curs.close()
    return result


def select_buffer(wkt, distance, buffer_params):
    curs = conn.cursor()
    try:
        if buffer_params:
            curs.execute("""
                SELECT ST_AsText(ST_Buffer(ST_GeomFromText(%s), %s, %s));
            """, (wkt, distance, buffer_params, ))
        else:
            curs.execute("""
                SELECT ST_AsText(ST_Buffer(ST_GeomFromText(%s), %s));
            """, (wkt, distance, ))
        result = (str(curs.fetchone()[0]), False, )
    except psycopg2.InternalError, e:
        result = (str(e), True, )
    curs.close()
    return result


def select_one_geom(function_name, wkt):
    curs = conn.cursor()
    try:
        curs.execute("""
            SELECT ST_AsText({}(ST_GeomFromText(%s)));
        """.format(function_name), (wkt,))
        result = (str(curs.fetchone()[0]), False, )
    except psycopg2.InternalError, e:
        result = (str(e), True, )
    curs.close()
    return result


def select_one_geom_return_text(function_name, wkt):
    curs = conn.cursor()
    try:
        curs.execute("""
            SELECT {}(ST_GeomFromText(%s));
        """.format(function_name), (wkt,))
        result = (str(curs.fetchone()[0]), False, )
    except psycopg2.InternalError, e:
        result = (str(e), True, )
    curs.close()
    return result


def select_scale(wkt, scale_x, scale_y):
    curs = conn.cursor()
    try:
        curs.execute("""
            SELECT ST_AsText(ST_Scale(ST_GeomFromText(%s), %s, %s));
        """, (wkt, scale_x, scale_y, ))
        result = (str(curs.fetchone()[0]), False, )
    except psycopg2.InternalError, e:
        result = (str(e), True, )
    curs.close()
    return result
