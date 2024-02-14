PURPOSE

Natural Query Language is a simple boolean predicate language which 
enables LLMs to reliably convert natural language into a parseable query language. NQL's purpose 
is not to do querying itself, but to be a domain-independent query language, intended to be parsed
into a target language for actual domain specific data querying, such as MySQL or ElasticSearch.

The goal is to enable 100% reliability for use with general LLMs, allowing general implementation
of Natural Language Query for machine learning laymen.

INSTALL
* todo: pip notes

Intellij syntax highlighting via https://github.com/lark-parser/intellij-syntax-highlighting

TODO
NQL
* NULL exists support

ES
* terms
* range
* exists
* query optimization: combine queries at same level which can be combined
* mapping type coersion
* child/parent relationships
* null/exists behaviors with not