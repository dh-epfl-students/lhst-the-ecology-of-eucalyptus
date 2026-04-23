from rapidfuzz import fuzz
from nltk import tokenize

def import_text(ark, context, size=50, separated_contexts=True):
    #Keep only paragraphs with "eucalyptus" in them
    if context == "paragraph":
        with open(f"../data/corpus_txt/{ark}.txt", "r", encoding='utf-8') as f:
            text = f.readlines()
        #text = [paragraph for paragraph in text if "eucalyp" in paragraph.lower() or "eucalip" in paragraph.lower() or "encalyp" in paragraph.lower()]
        end_text = [paragraph for paragraph in text if fuzz.token_set_ratio("eucalyptus", paragraph.lower()) > 90]

        #merge contexts through "\n" to have a single text
        #TODO: handle better several occurences?
        end_text = "\n".join(end_text)
        return end_text
    
    #Keep only a certain context window around the word "eucalyptus"
    #TODO: check for handling paragraphs
    #TODO: handle better several occurences (what if eucalyptus is in the context of another?)
    elif context == "context_window":
        with open(f"../data/corpus_txt/{ark}.txt", "r", encoding='utf-8') as f:
            #TODO: check if losing "\n" (paragraph) context is important or not
            text = f.read().split()
        
        #separate text into tokens, get a window of {size} in each side of "eucalyptus"
        tokens_context = []
        for i, word in enumerate(text):
            #if "eucalyp" in word.lower() or "eucalip" in word.lower() or "encalyp" in word.lower():
            if fuzz.ratio("eucalyptus", word.lower()) > 75 or "eucalypt" in word.lower() or "encalypt" in word.lower() or "eucalipt" in word.lower():
                new_text = text[i-size:i] + ["eucalyptus"] + text[i+1:i+size]
                tokens_context.append(new_text)


        #merge text within each occurence, then merge paragraphs with "\n"
        end_text = []
        for context in tokens_context:
            end_text.append(" ".join(context))
            
        if separated_contexts == False:
            end_text = "\n".join(end_text)

        else:
            return end_text

    elif context == "sentence":
        with open(f"../data/corpus_txt/{ark}.txt", "r", encoding='utf-8') as f:
            sentences = tokenize.sent_tokenize(f.read())

        sentence_context = []
        for i, sentence in enumerate(sentences):
            if fuzz.ratio("eucalyptus", sentence.lower()) > 75 or "eucalyp" in sentence.lower() or "encalypt" in sentence.lower() or "eucalipt" in sentence.lower():
                if size == 0:
                    sentence_context.append(sentence)
                else:
                    sentence_context.append(sentences[i-size:i+size])
                    


        #merge text within each occurence, then merge paragraphs with "\n"
        end_text = []
        for context in sentence_context:
            if size != 0:
                end_text.append(" ".join(context))
            else:
                end_text = sentence_context
            
        if separated_contexts == False:
            end_text = "\n".join(end_text)

        else:
            return end_text  

    else:
        raise ValueError('context must be either "paragraph", "context_window" or "sentence"')