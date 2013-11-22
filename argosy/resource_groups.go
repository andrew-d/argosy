package main

import (
    "fmt"
    "github.com/codegangsta/martini"
    "github.com/jmoiron/sqlx"
    "net/http"
)

type Group struct {
    Id   int64  `db:"group_id" json:"id"`
    Name string `db:"name"     json:"name"`
}

func init() {
    setupRegistry = append(setupRegistry, setupGroups)
}

func setupGroups(m *martini.ClassicMartini) {
    m.Post("/groups", func(req *http.Request, w http.ResponseWriter, db *sqlx.DB) {
        // Try to find this group.
        name := req.FormValue("name")
        rows, err := db.NamedQueryMap(`SELECT * FROM groups WHERE name = :name`,
            map[string]interface{}{
                "name": name,
            })
        if err != nil {
            panic(err)
            return
        }

        exists := false
        group := Group{}
        if rows.Next() {
            // Already have it!
            err = rows.StructScan(&group)
            if err != nil {
                panic(err)
            }
            exists = true
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
        }

        fmt.Fprint(w, JsonResponse{"id": group.Id, "name": name, "exists": exists})
    })
}
