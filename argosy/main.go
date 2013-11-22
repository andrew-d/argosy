package main

// https://github.com/nfnt/resize
import (
    "database/sql"
    "fmt"
    "github.com/codegangsta/martini"
    "github.com/stvp/go-toml-config"
    "net/http"
    "os"

    _ "github.com/lib/pq"
    _ "github.com/mattn/go-sqlite3"

    "github.com/jmoiron/sqlx"
)

type Item struct {
    Hash       string `db:"item_id"     json:"id"`
    CreatedOn  int64  `db:"created_on"  json:"created_on"`
    FileSize   int64  `db:"file_size"   json:"file_size"`
    Width      int    `db:"width"       json:"width"`
    Height     int    `db:"height"      json:"height"`
    IsAnimated bool   `db:"is_animated" json:"is_animated"`

    GroupId    sql.NullInt64 `db:"group_id"    json:"group_id"`
    GroupIndex sql.NullInt64 `db:"group_index" json:"group_index"`
}

var (
    host = config.String("host", "localhost")
    port = config.Int("port", 8000)

    db_dialect = config.String("db.dialect", "sqlite3")
    db_params  = config.String("db.params", "/tmp/test.db")
)

var setupRegistry []func(*martini.ClassicMartini)

func main() {
    // If we have a configuration variable given, read and parse it.
    config_path := os.Getenv("ARGOSY_CONFIG")
    if config_path != "" {
        if err := config.Parse(config_path); err != nil {
            panic(err)
        }
    }

    // The main app.
    m := martini.Classic()

    // Inject database
    db, err := sqlx.Open(*db_dialect, *db_params)
    if err != nil {
        panic(err.Error())
    }
    defer db.Close()
    m.Map(db)

    // Set up schema
    db.Execf(schema)

    // We return JSON by default.
    m.Use(func(res http.ResponseWriter, req *http.Request) {
        res.Header().Set("Content-Type", "application/json; charset=utf-8")
    })

    // For each route, set it up.
    for _, f := range setupRegistry {
        f(m)
    }

    fmt.Printf("[martini] Listening on %s:%d\n", *host, *port)
    http.ListenAndServe(fmt.Sprintf("%s:%d", *host, *port), m)
}
