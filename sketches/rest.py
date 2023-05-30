from fastapi import FastAPI, HTTPException
import psycopg2, psycopg2.extras

app = FastAPI()

conn = psycopg2.connect("host=uta.biocommons.org dbname=uta user=anonymous password=anonymous")



# What a get method would look like

@app.get("/seq/{ac}/{start_i}/{end_i}", status_code=200)
async def get_seq(self, ac, start_i=None, end_i=None):
    # Code to check if the sequence is in the databse or not
    # If so,
    if(...):
        # Exception already written "Failed to fetch <ac>..." in seqfetcher
        raise HTTPException(
            status_code=404,
            detail="Failed to fetch..."
        )
    # We need to import a bunch of other packages from hgvs 
    # for this to work.
    return self.seqfetcher.fetch_seq(ac, start_i, end_i)
