package main

import (
    "encoding/json"
)

type JsonResponse map[string]interface{}

func (r JsonResponse) String() string {
    return Jsonify(r)
}

func Jsonify(obj interface{}) string {
    b, err := json.Marshal(obj)
    if err != nil {
        return ""
    }
    return string(b)
}
