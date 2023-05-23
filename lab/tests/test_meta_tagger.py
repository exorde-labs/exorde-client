import pytest, json

from exorde_meta_tagger import meta_tagger_initialization, tag, zero_shot
from aiosow.autofill import autofill
from .sample import SAMPLE

CONFIG = meta_tagger_initialization()


def test_max_depth_is_set():
    assert CONFIG["max_depth"] == 2
    print("assert max_depth ok")


@pytest.mark.asyncio
async def test_result_of_tag_should_be_json_serializable():
    """Result requires to be serialiable to pass trough the network."""
    test_content = SAMPLE[:1]
    result = await autofill(tag, args=[test_content], memory=CONFIG)
    tag_result = json.dumps(result)
    print("got tag result")
    with open("tag-result.json", "w") as f:
        f.write(tag_result)


@pytest.mark.asyncio
async def test_result_of_zero_shot_should_be_json_serializable():
    """Result requires to be serialiable to pass trough the network."""
    test_content = SAMPLE[:1]
    print("starting zero_shot")
    result = await autofill(zero_shot, args=[test_content], memory=CONFIG)
    zero_shot_result = json.dumps(result)
    print("got zero_shot result")
    with open("zero_shot-result.json", "w") as f:
        f.write(zero_shot_result)
        
        
from exorde_data import Item
import time
import itertools
def chunked(it, size):
   it = iter(it)
   while True:
      p = tuple(itertools.islice(it, size))
      if not p:
         break
      yield p
def test_input_output():    
    init = meta_tagger_initialization()

    ### TEST ZONE
    test_samples = ["Texas Governor Greg Abbott has made it VERY clear he will NOT under any circumstances SIGN any “COMMON SENSE GUN LAWS”! Common Sense is NOT allowed in Texas anymore as DECRED by Greg Abbott who has never had any & he’s OK with DEAD TEXANS BODIES lying SLANDERED by some 18 yr old!",
        "Yesterday in Orange, I ate an orange in front of the Orange shop, with the mayor who was returning from the sea with his mother",
       "Get the best deal on laptops! Save up to 50% on our online store!",
        "U.S. Federal Reserve announces a 0.25% increase in interest rates",
        "Introducing our new line of skincare products - rejuvenate your skin!",
        "Microsoft acquires another startup, expanding its cloud services",
        "Try our 30-day free trial of premium membership, and enjoy unlimited access!",
        "Oil prices continue to surge amid geopolitical tensions",
        "Eager to travel again? Book your dream vacation now with our special discounts!"
        "Bitcoin hits new record high of $70,000"
        ]
    
    test_samples = [preprocess_text(e, remove_stopwords=False) for e in test_samples]
    test_samples = test_samples
    print("number of samples = ", len(test_samples))
    # Create a list to store the fabricated items
    items = []

    # Iterate over the test_samples and create an Item object for each sample
    for sample in test_samples:
        item = Item()
        item.content = sample
        items.append(item)
        assert(len(item.content)>0)

    temps_debut_total = time.perf_counter()
    CHUNK_SIZE_TAG = 1000
    CHUNK_SIZE_ZEROSHOT = 1

    temps_debut_total = time.perf_counter()
    print("\n\n****** METADATA TAG TESTING *****")
    for i, items_chunk in enumerate(chunked(items, CHUNK_SIZE_TAG)):
        # Record the start time
        start_time = time.time()

        temps_debut = time.perf_counter()
        for item in items_chunk:
            assert isinstance(item, Item)

        items_chunk = tag(items_chunk, init["nlp"], init["device"], init["mappings"]) 

        for item in items_chunk:
            assert isinstance(item, Item)
            
            if i == 0:
                # Print the null attributes
                print("Null attributes post tag:")
                null_attributes = [attr for attr in dir(item) if getattr(item, attr) is None]
                for attr in null_attributes:
                    print(attr)

        temps_fin = time.perf_counter()
        temps_execution =  round(temps_fin - temps_debut,2)
        frequence_processeur = os.cpu_count() * 10**6
        cycles_cpu = round(temps_execution * frequence_processeur,0)
        print(f"Execution time: {temps_execution} seconds")
        # print(f"Cycle CPU: {cycles_cpu}")
    

    temps_fin_total = time.perf_counter()
    temps_execution_total = round(temps_fin_total - temps_debut_total)
    print(f"\nTotal  Execution time: {temps_execution_total} seconds")
    
    tag_tot_time = temps_execution_total
    print("\n\n****** ZEROSHOT CLASSIFICATION TESTING *****")
    for i,item in enumerate(items):
        # Record the start time
        start_time = time.time()
        temps_debut = time.perf_counter()
        assert isinstance(item, Item)
        item = zero_shot(item, init["labeldict"], init["classifier"], max_depth=2)
        assert isinstance(item, Item)
    
        if i == 0:
            # Print the null attributes
            print("Null attributes post zero_shot:")
            null_attributes = [attr for attr in dir(item) if getattr(item, attr) is None]
            for attr in null_attributes:
                print(attr)

        assert item.classification is not None
    
    temps_fin_total = time.perf_counter()
    temps_execution_total = round(temps_fin_total - temps_debut_total)
    zs_tot_time = temps_execution_total

    temps_par_char_total_zs = round(temps_execution_total / sum(len(s) for s in test_samples),4)
    print("Number of samples = ", len(test_samples))
    print(f"\n\nTotal TAGGING Execution time: {tag_tot_time} seconds")
    print(f"Total ZEROSHOT Execution time: {zs_tot_time} seconds")
