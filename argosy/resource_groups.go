package main

import (
    "github.com/codegangsta/martini"
    "github.com/coopernurse/gorp"
    "net/http"
    "strconv"
)

type Group struct {
    Id   int64  `db:"group_id" json:"id"`
    Name string `db:"name"     json:"name"`
}

func listAllGroups(dbmap *gorp.DbMap) []Group {
    var groups []Group
    _, err := dbmap.Select(&groups, `SELECT * FROM groups ORDER BY group_id ASC`)
    if err != nil {
        panic(err.Error())
    }
    return groups
}

func getOneGroup(dbmap *gorp.DbMap, id int64) *Group {
    obj, err := dbmap.Get(Group{}, id)
    if err != nil {
        panic(err)
    }

    if obj == nil {
        return nil
    } else {
        return obj.(*Group)
    }
}

func findGroup(dbmap *gorp.DbMap, name string) *Group {
    var test []Group
    _, err := dbmap.Select(&test, `SELECT * FROM groups WHERE name = `+BindVar(1)+` LIMIT 1`, name)
    if err != nil {
        panic(err)
    }

    if len(test) > 0 {
        return &test[0]
    } else {
        return nil
    }
}

func findOrCreateGroup(dbmap *gorp.DbMap, name string) (*Group, bool) {
    group := findGroup(dbmap, name)
    if group != nil {
        return group, false
    }

    group = &Group{Name: name}
    err := dbmap.Insert(group)
    if err != nil {
        panic(err)
    }

    return group, true
}

func init() {
    registerInit(setupGroups)
}

func setupGroups(m *martini.ClassicMartini) {
    m.Get("/groups", func(dbmap *gorp.DbMap) string {
        return JsonResponse{"groups": listAllGroups(dbmap)}.String()
    })
    m.Get("/groups/:id", func(dbmap *gorp.DbMap, params martini.Params) (int, string) {
        id, err := strconv.ParseInt(params["id"], 10, 64)
        if err != nil {
            return http.StatusBadRequest, JsonResponse{"error": "bad id"}.String()
        }

        g := getOneGroup(dbmap, id)
        if g != nil {
            return http.StatusOK, Jsonify(g)
        } else {
            // TODO: better error
            return http.StatusNotFound, JsonResponse{"found": false}.String()
        }
    })
    m.Put("/groups/:id", func(req *http.Request, dbmap *gorp.DbMap, params martini.Params) (int, string) {
        id, err := strconv.ParseInt(params["id"], 10, 64)
        if err != nil {
            return http.StatusBadRequest, JsonResponse{"error": "bad id"}.String()
        }

        group := getOneGroup(dbmap, id)
        if group == nil {
            // TODO: better error
            return http.StatusNotFound, JsonResponse{"found": false}.String()
        }

        // Do nothing if nothing is to be changed.
        newName := req.FormValue("name")
        if newName == group.Name {
            return http.StatusOK, Jsonify(group)
        }

        // Check if it already exists
        existing := findGroup(dbmap, newName)
        if existing != nil {
            return http.StatusConflict, Jsonify(existing)
        }

        // TODO: possible race
        group.Name = newName
        _, err = dbmap.Update(group)
        if err != nil {
            panic(err)
        }

        return http.StatusOK, Jsonify(group)
    })
    m.Post("/groups", func(req *http.Request, dbmap *gorp.DbMap) (int, string) {
        group, created := findOrCreateGroup(dbmap, req.FormValue("name"))
        if created {
            return http.StatusCreated, Jsonify(group)
        } else {
            return http.StatusConflict, Jsonify(group)
        }
    })
    m.Delete("/groups/:id", func(dbmap *gorp.DbMap, params martini.Params) (int, string) {
        id, err := strconv.ParseInt(params["id"], 10, 64)
        if err != nil {
            return http.StatusBadRequest, JsonResponse{"error": "bad id"}.String()
        }

        g := &Group{Id: id}
        count, err := dbmap.Delete(g)
        if err != nil {
            panic(err)
        }

        // We can tell if we deleted anything by the number of rows affected
        if count == 0 {
            return http.StatusNotFound, JsonResponse{"found": false}.String()
        } else {
            return http.StatusOK, JsonResponse{"id": id, "deleted": true}.String()
        }
    })
}
