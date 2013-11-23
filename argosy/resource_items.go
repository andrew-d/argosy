package main

import (
    "database/sql"
    "github.com/codegangsta/martini"
    "github.com/coopernurse/gorp"
    "net/http"
    "strconv"
)

type Item struct {
    Hash       string `db:"hash"        json:"id"`
    CreatedOn  int64  `db:"created_on"  json:"created_on"`
    FileSize   int64  `db:"file_size"   json:"file_size"`
    Width      int    `db:"width"       json:"width"`
    Height     int    `db:"height"      json:"height"`
    IsAnimated bool   `db:"is_animated" json:"is_animated"`

    GroupId    sql.NullInt64 `db:"group_id"    json:"group_id"`
    GroupIndex sql.NullInt64 `db:"group_index" json:"group_index"`
}

func getAllItems(dbmap *gorp.DbMap) []Item {
    var items []Item
    _, err := dbmap.Select(&items, `SELECT * FROM items ORDER BY created_on ASC`)
    if err != nil {
        panic(err.Error())
    }
    return items
}

func getOneItem(dbmap *gorp.DbMap, id string) *Item {
    obj, err := dbmap.Get(Item{}, id)
    if err != nil {
        panic(err)
    }

    if obj == nil {
        return nil
    } else {
        return obj.(*Item)
    }
}


func init() {
    registerInit(setupItems)
}


func setupItems(m *martini.ClassicMartini) {
    m.Get("/items", func(dbmap *gorp.DbMap) string {
        return JsonResponse{"item": getAllItems(dbmap)}.String()
    })
    m.Get("/items/:id", func(dbmap *gorp.DbMap, params martini.Params) (int, string) {
        id := params["id"]
        if len(id) != 32 {
            return http.StatusBadRequest, JsonResponse{"error": "bad id"}.String()
        }

        i := getOneItem(dbmap, id)
        if i != nil {
            return http.StatusOK, Jsonify(i)
        } else {
            // TODO: better error
            return http.StatusNotFound, JsonResponse{"found": false}.String()
        }
    })
    m.Put("/items/:id", func(req *http.Request, dbmap *gorp.DbMap, params martini.Params) (int, string) {
        id := params["id"]
        if len(id) != 32 {
            return http.StatusBadRequest, JsonResponse{"error": "bad id"}.String()
        }

        item := getOneItem(dbmap, id)
        if item == nil {
            // TODO: better error
            return http.StatusNotFound, JsonResponse{"found": false}.String()
        }

        // Update the item from the input form.
        // TODO: what's allowd to be updated here?
        // TODO: what happens when tags are updated?
        idx, err := strconv.ParseInt(req.FormValue("group_index"), 10, 64)
        if err != nil {
            return http.StatusBadRequest, JsonResponse{"error": "bad group index"}.String()
        }
        item.GroupIndex.Int64 = idx
        item.GroupIndex.Valid = true

        return http.StatusOK, JsonResponse{"item": item}.String()
    })
    m.Post("/items", func(req *http.Request, dbmap *gorp.DbMap) (int, string) {
        // Uploads must go through another route.
        return http.StatusForbidden, ""
    })
    m.Delete("/items/:id", func(dbmap *gorp.DbMap, params martini.Params) (int, string) {
        id := params["id"]
        if len(id) != 32 {
            return http.StatusBadRequest, JsonResponse{"error": "bad id"}.String()
        }

        i := &Item{Hash: id}
        count, err := dbmap.Delete(i)
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
