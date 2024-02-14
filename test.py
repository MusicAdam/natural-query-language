import nql

converter = nql.EsConverter("contacts")
es_dsl = converter.convert(
  """
    AND(
      "contact.gifts[*].amount">"100",
      "contact.gifts[*].occurred_at">"2023-02-13"
    )
  """
)

print(es_dsl)