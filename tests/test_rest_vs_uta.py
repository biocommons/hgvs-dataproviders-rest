import utarest
import hgvs.dataproviders.uta as uta

conn_uta = uta.connect()
conn_uta_rest = utarest.connect()

print(conn_uta.get_gene_info("VHL"))
print(conn_uta_rest.get_gene_info("VHL"))