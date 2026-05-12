
def import_text(ark, context, size=50, separated_contexts=True):
    from rapidfuzz import fuzz
    from nltk import tokenize
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
    

def plot_histogram(df, x, y, weights="document", normalize=False, columns_to_remove=False, column_order=False, row_order = False):
    import itertools
    import pandas as pd
    import matplotlib.pyplot as plt
    from scipy.stats import chi2_contingency
    if weights == "document":
        #Create dict with all possible metadata types and with a list with the topics length
        cross_tab = dict()
        for metadata_type in df[x].unique():
            single_type = dict()
            for topic in list(itertools.chain.from_iterable(df[y])):
                single_type[topic] = 0
            cross_tab[metadata_type] = single_type

        for _, row in df.iterrows():
            topic_list = row[y]
            if columns_to_remove:
                topic_list = [topic for topic in topic_list if topic not in columns_to_remove]

            for topic in topic_list:
                #int(topic) + 1 is because of -1 topic that shifts everyone by "1"
                cross_tab[row[x]][topic] += 1 / len(topic_list)

        cross_tab = pd.DataFrame(cross_tab)

        if row_order:
            cross_tab = cross_tab[row_order]
            cross_tab = cross_tab.T
        else:
            cross_tab = cross_tab.T
            cross_tab = cross_tab.sort_index(axis=0)

        if columns_to_remove:
            cross_tab = cross_tab.drop(columns_to_remove, axis=1)

        if column_order:
            cross_tab = cross_tab[column_order]

        if normalize:
            cross_tab = cross_tab.div(cross_tab.sum(axis=1), axis=0)

        ax = cross_tab.plot(kind='bar', stacked=True, rot=0)
        ax.legend(title=y, bbox_to_anchor=(1, 1.02), loc='upper left')
        plt.xticks(rotation=60)
        plt.title(f"Distribution of {y} based on {x} - Weighted by documents")
        plt.show()
        
    elif weights == "context":
        #Explode dataframe based on row and turn it into a crosstab
        exploded_df = df.explode(y).reset_index().drop("index", axis=1)
        exploded_df = exploded_df.sort_index(axis=0)

        if columns_to_remove:
            exploded_df = exploded_df[exploded_df["metatopics"].isin(columns_to_remove) == False]

        if normalize:
            cross_tab = pd.crosstab(exploded_df[x], exploded_df[y], normalize="index")
        else:
            cross_tab = pd.crosstab(exploded_df[x], exploded_df[y])

        if column_order:
            cross_tab = cross_tab[column_order]

        if row_order:
            cross_tab = cross_tab.T
            cross_tab = cross_tab[row_order]
            cross_tab = cross_tab.T
        else:
            cross_tab = cross_tab.sort_index(axis=0)

        ax = cross_tab.plot(kind='bar', stacked=True, rot=0)
        ax.legend(title=y, bbox_to_anchor=(1, 1.02), loc='upper left')
        plt.xticks(rotation=60)
        plt.title(f"Distribution of {y} based on {x} - Weighted by contexts")
        plt.show()
        
    else:
        print('weights argument must be either "document" or "context"')
        return
    

    # return chi-square test between each distribution:
    # test chi-2:
    data = [i for i, row in cross_tab.iterrows()]
    for combination in itertools.combinations(data, 2):
        first_row = cross_tab.loc[combination[0]]
        second_row = cross_tab.loc[combination[1]]
        stat, p, dof, expected = chi2_contingency([first_row.to_list(), second_row.to_list()])

        # interpret p-value
        alpha = 0.05
        print(f"________________")
        print(f"comparision between: {combination[0]} and {combination[1]}")
        print("p value is " + str(p))
        if p <= alpha:
            print('Dependent (reject H0)')
        else:
            print('Independent (H0 holds true)')
