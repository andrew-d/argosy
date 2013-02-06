# Todo

## Goals

- Store various types of media files (i.e. uploaded to and stored on server)
- Allow tagging and grouping for all media types
  - Also, searching
- Support extracting data from certain media types for searching (using Postgres's full-text search)
- Support extracting generic metadata from media types for display (e.g. picture size, words in document, etc.)
  - Not sure if this should be searchable.  Default to 'no' for now.

## General Planning

- We have a generic upload interface for media
- Each media type can be registered to handle a specific list of MIME types

- Each media type needs the following
  - Storage (in a flat file, in the DB, etc)
  - Optional
