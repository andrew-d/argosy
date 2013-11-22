package main

import (
    "encoding/json"
)

type JsonResponse map[string]interface{}

func (r JsonResponse) String() string {
    b, err := json.Marshal(r)
    if err != nil {
        return ""
    }
    return string(b)
}
