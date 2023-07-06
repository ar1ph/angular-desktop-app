import statistics
import os, sys
from tabulate import tabulate
from tqdm import tqdm

sys.path.append('..')
# Import the embeding model and database class
# From the embeddings and vectorstores directory
from embeddings.HuggingFaceEmbedding import HuggingFaceEmbedding
from vectorstores.Chroma import Chroma
#from vectorstores.Milvus import Milvus

class Combination(object):

    def __init__(self,
                 db_model,
                 queries_path : str,
                 queries_map: dict
                 ) -> None:
        
        self.db_model = db_model
        self.queries_path = queries_path
        self.queries_map = queries_map



    def get_query_source_map(self) -> dict[str, list[str]]:
        """
        Retrieves a mapping of queries to their corresponding sources.
        
        Returns:
            A dictionary mapping queries to sources.
        """
        qa = dict()
        contents = None
        import json
        
        # Load the contents of the queries file
        with open(file=self.queries_path, mode='r') as fn:
            contents = json.load(fn)
            
        # Iterate over each query collection
        for qa_collection in contents:
            query = qa_collection['query']
            var_dict = qa_collection['variables']
            variables = list(var_dict.keys())
            sources = qa_collection['sources']
            num_of_instances = len(var_dict[variables[0]])
            
            # Iterate over each instance of the query
            for idx in range(num_of_instances):
                instance = dict()
                
                # Create an instance dictionary by assigning 
                # the values of the variables
                for var in variables:
                    instance[var] = var_dict[var][idx]
                
                # Generate the question by formatting the query 
                # with the instance variables
                question = query.format(**instance)
                
                # Map the question to its corresponding source
                qa[question] = sources[idx]
        print(f"{'-QA-'*24}",qa)
        return qa


    
    def get_sources(self, 
                    query: str
                    ) -> list[str]:
        """
        Retrieves a list of sources associated with the given query.
        
        Args:
            query (str): The query to be executed.
        
        Returns:
            A list of source filenames associated with the query.
        """
        db = self.db_model
        
        # Execute the query and retrieve the output
        output = db.query(query, -1, include=['metadatas', 'distances'])
        
        # Extract the metadatas from the output
        metadatas = output['metadatas'][0]
        
        sources = []
        
        # Iterate over each metadata and extract the source filename
        for metadata in metadatas:
            sources.append(os.path.basename(metadata['source']))
        
        return sources

    
    def get_k(self, 
              query: str, 
              sources: list[str], 
              matches: int
              ) -> int:
        """
        Retrieves the value of 'k' based on the number of matches for a given query.
        
        Args:
            query (str): The query to be executed.
            sources (list): A list of source filenames to match against.
            matches (int): The desired number of filename matches.
        
        Returns:
            int: The value of 'k' representing the minimum number of output files
                 to get the required number of filename 'matches'.
        
        Raises:
            Exception: If the number of unique sources is more than the 
                       provided number of matches.
        """
        # Retrieve the output sources associated with the query
        output_sources = self.get_sources(query=query)
        
        # Create a set of the given sources to check for matches
        given_sources = set(sources)
        
        # Iterate over the output sources and check for matches
        for idx, src in enumerate(output_sources):
            if src in given_sources:
                matches -= 1
                
                # If the desired number of matches is reached, return the value of 'k'
                if matches == 0:
                    return idx + 1
        
        # Raise an exception if the number of unique sources is more than the number of matches
        raise Exception(f"Number of unique sources doesn't match the number of matches: {query}")

        
    
    def get_report(self, 
                   matches: int
                   ) -> dict[str, str | float | int]:
        """
        Generates a report containing various statistics based on the matches for different queries.
        
        Args:
            matches (int): The desired number of matches for each query.
        
        Returns:
            dict: A dictionary containing the report with the following keys:
                - 'Embedding Model': The name of the embedding model.
                - 'DB Type': The type of the database model.
                - 'Strategy': The strategy used by the database model.
                - 'Average k': The average value of 'k'.
                - 'Sigma': The standard deviation of the values of 'k'.
        """
        all_k = []
        
        # Retrieve the mapping of queries to sources 
        #query_srcs_map = self.get_query_source_map()

        #If query source map is directly passed through frontend
        query_srcs_map = self.queries_map
        
        # Initialize a progress bar to track the values of 'k'
        with tqdm(total=len(query_srcs_map.items()),
                desc="Getting the values of k: ",
                ncols=100) as pbar_k:
            for query, sources in query_srcs_map.items():
                # Get the value of 'k' for each query and append it to the list
                all_k.append(self.get_k(query=query, sources=sources, matches=matches))
                pbar_k.update()

        # Calculate average 'k' and sigma
        avg = round(sum(all_k) / len(all_k))
        sigma = round(statistics.stdev(all_k), 2)
        
        # Build the report dictionary
        report = {'Embedding Model': self.db_model.emb_model_name,
                'DB Type': self.db_model.name,
                'Strategy': self.db_model.strategy,
                'Average k': avg,
                'Sigma': sigma}
        
        return report

    

    def save_reports(self, 
                     all_reports: list[dict[str, str | int | float]],
                     file_path: str
                     ) -> None:
        """
        Saves the reports to a file in a tabular format.
        
        Args:
            all_reports (list): A list of dictionaries containing the reports.
            file_path (str): The path to the file where the reports will be saved.
        """
        row = ['Embedding Model', 'DB Type', 'Strategy', 'Average k', 'Sigma', 'Frequency']
        
        # Check if the file already exists
        if not os.path.exists(file_path):
            with open(file=file_path, mode='w') as fn:
                # Write the column names as the first line
                fn.write(' '.join(row))
                fn.write('\n\n')
        
        # Read existing lines from the file, if any
        with open(file_path, "r") as file:
            lines = file.readlines()
            data = [row]
            for line in lines[2:]:
                # Parse each line and extract row values
                row = [word.strip() for word in line.strip().split('|') if len(word.strip()) > 0]
                data.append(row)
        
        # Append the new report data to the existing data
        for report in all_reports:
            data.append(list(report.values()))
        
        # Format the data as a table using the tabulate library
        table = tabulate(data, headers="firstrow", tablefmt="pipe")
        
        # Write the table to the file
        with open(file_path, "w") as file:
            file.write(table)



def main():
    # Initialize embedding model using models in embeddings directory
    emb_model = HuggingFaceEmbedding("all-MiniLM-L6-v2")
    # Initialize database model using the database in vectorstores directory
    db_model = Chroma(embedding=emb_model,
                      strategy="ip")
    # Add embeddings to the database
    data_directory = os.path.join(os.path.abspath(os.pardir),
                                  'data_temp')
    db_model.add_data(data_directory=data_directory)
    # Initialize the combination model using the database and queries file
    assets_directory = os.path.join(os.path.abspath(os.pardir),
                                    "assets")
    queries_path = os.path.join(assets_directory, 'queries_temp.json')
    combination = Combination(db_model=db_model,
                              queries_path=queries_path,
                              queries_map={})
    # Get the report (statistics) based on the provided datas and queries
    reports = [combination.get_report(matches=1)]
    # TODO: Need to add the number of documents in the report properly
    reports[0]['Frequency'] = 3
    combination.save_reports(all_reports=reports,
                             file_path=os.path.join(os.path.abspath(os.pardir),
                                                    os.path.join("benchmark", "benchmark.txt")))
    
        


if __name__ ==  "__main__": main()