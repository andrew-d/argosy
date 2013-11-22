package main

import (
    "github.com/codegangsta/martini"
    "github.com/jmoiron/sqlx"
    "net/http"
)

type Group struct {
    Id   int64  `db:"group_id" json:"id"`
    Name string `db:"name"     json:"name"`
}

func listAllGroups(w http.ResponseWriter, db *sqlx.DB) string {
    groups := []Group{}
    err := db.Select(&groups, `SELECT * FROM groups ORDER BY group_id ASC`)
    if err != nil {
        panic(err.Error())
    }

    return JsonResponse{"groups": groups}.String()
}

func getOneGroup(w http.ResponseWriter, db *sqlx.DB, params martini.Params) (int, string) {
    // Try to find this group.
    rows, err := db.NamedQueryMap(`SELECT * FROM groups WHERE group_id = :id`,
        map[string]interface{}{
            "id": params["id"],
        })
    if err != nil {
        panic(err)
    }

    if rows.Next() {
        group := Group{}
        err = rows.StructScan(&group)
        if err != nil {
            panic(err)
        }

        return http.StatusOK, Jsonify(group)
    } else {
        // TODO: better error
        return http.StatusNotFound, JsonResponse{"found": false}.String()
    }
}

func updateOneGroup(req *http.Request, w http.ResponseWriter, db *sqlx.DB, params martini.Params) string {
    // Try to find this group.
    rows, err := db.NamedQueryMap(`SELECT group_id FROM groups WHERE group_id = :id`,
        map[string]interface{}{
            "id": params["id"],
        })
    if err != nil {
        panic(err)
    }

    if !rows.Next() {
        // TODO: do we allow directly creating a group that doesn't exist?
        return JsonResponse{"found": false}.String()
    }

    name := req.FormValue("name")
    _, err = db.NamedExecMap(`UPDATE groups SET name = :name WHERE group_id = :id`,
        map[string]interface{}{
            "id":   params["id"],
            "name": name,
        })
    if err != nil {
        panic(err)
    }

    return JsonResponse{"id": params["id"], "name": name}.String()
}

func createGroup(req *http.Request, w http.ResponseWriter, db *sqlx.DB) (int, string) {
    name := req.FormValue("name")
    rows, err := db.NamedQueryMap(`SELECT * FROM groups WHERE name = :name`,
        map[string]interface{}{
            "name": name,
        })
    if err != nil {
        panic(err)
    }

    var status int
    group := Group{}

    if rows.Next() {
        // Already have it!
        err = rows.StructScan(&group)
        if err != nil {
            panic(err)
        }
        status = http.StatusConflict
    } else {
        // Save name in group, save to DB
        group.Name = name
        res, err := db.NamedExec(`INSERT INTO groups (name) VALUES (:name)`, group)
        if err != nil {
            panic(err.Error())
        }

        iid, err := res.LastInsertId()
        if err != nil {
            panic(err.Error())
        }
        group.Id = iid
        status = http.StatusCreated
    }

    return status, Jsonify(group)
}

func deleteGroup(w http.ResponseWriter, db *sqlx.DB, params martini.Params) string {
    // TODO: this doesn't work, get database locked error
    _, err := db.NamedExecMap(`DELETE FROM groups WHERE group_id = :id`,
        map[string]interface{}{
            "id": params["id"],
        })
    if err != nil {
        panic(err)
    }

    return JsonResponse{"id": params["id"], "deleted": true}.String()
}

func init() {
    registerInit(setupGroups)
}

func setupGroups(m *martini.ClassicMartini) {
    m.Get("/groups", listAllGroups)
    m.Get("/groups/:id", getOneGroup)
    m.Put("/groups/:id", updateOneGroup)
    m.Post("/groups", createGroup)
    m.Delete("/groups/:id", deleteGroup)
}
