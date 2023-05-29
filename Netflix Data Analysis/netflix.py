import PyMovieDb
import pandas as pd
import requests
import random
import re
import seaborn as sns
import matplotlib.pyplot as plt


"""Auxiliary Functions"""


def Complement_Color(Color):
    Color = Color[1:]
    Color = int(Color, 16)
    Complementary_Color = 0xFFFFFF - Color
    Complementary_Color = "#%06X" % Complementary_Color
    return Complementary_Color


def Check_Column_Emptiness(Dataset, Column_Name):
    if len(Dataset[Column_Name].value_counts()) > 1:
        return False
    return True


"""Web scraping functions to get movie ID and rating"""


def Get_Movie_IDs(Dataset, Flag):
    if Flag:
        Movie_IDs = Obtain_Movie_ID_List_From_Movie_Names(Dataset)
        Dataset.iloc[:, 13] = Movie_IDs
        Dataset.to_excel("Netflix Titles.csv", sheet_name='Netflix Titles')
    else:
        Movie_IDs = Dataset.iloc[:, 13]
    return Movie_IDs


def Get_Ratings(Dataset, IDs, Flag):
    if Flag:
        Ratings = Get_Rating_Using_Movie_ID(Dataset, IDs)
        Dataset.iloc[:, 12] = Ratings
        Dataset.to_excel("Netflix Titles.csv", sheet_name='Netflix Titles')
    else:
        Ratings = Dataset.iloc[:, 12]
    return Ratings


def Obtain_Movie_ID_List_From_Movie_Names(Dataset):
    Movie_IDs = []
    imdb = PyMovieDb.IMDB()
    for row_number in range(10):
        resultList = imdb.search(Dataset.iloc[row_number, 2], int(Dataset.iloc[row_number, 7]))
        Result_Split = resultList.split()
        Found = False
        for j in Result_Split:
            if re.match("^\"tt", j):
                Movie_ID = j.strip(",\"")
                Found = True
                break
        if Found is True:
            Movie_IDs.append(Movie_ID)
        else:
            Movie_IDs.append("NotFound/Unavailable")
    return Movie_IDs


def Get_Rating_Using_Movie_ID(Dataset, IDs):
    Ratings_List = []
    for index in range(0, Dataset.shape[0]):
        if re.match("NotFound/Unavailable", IDs[index]):
            Ratings_List.append("NaN")
        else:
            url = "https://www.imdb.com/title/" + IDs[index]
            header = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36'
                                    ' (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
                      'Accept-Encoding': '*',
                      'Connection': 'keep-alive'}
            page = requests.get(url, headers=header)
            rating = re.search('<span class="sc-bde20123-1 iZlgcd">(...)</span>', page.text)
            if rating:
                Ratings_List.append(float(rating.group(1)))
            else:
                Ratings_List.append("NaN")
    Dataset.iloc[:, 12] = Ratings_List
    Dataset.to_excel("Netflix Titles.csv", sheet_name='Netflix Titles')
    return Ratings_List


"""Plot Functions"""


def Count_Plot(data, y, order, Figure_Name, x_label, y_label):
    plt.figure(Figure_Name, figsize=(10, 5))
    plt.title(Figure_Name)
    plot = sns.countplot(y=y, data=data, order=order)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    for i in plot.containers:
        plot.bar_label(i, )
    plt.subplots_adjust(left=0.3)
    plot.set_xlim(0, max(data[y].value_counts()) + 5)


def Line_Plot(data, x, y, Figure_Name, x_label, y_label):
    plt.figure(Figure_Name, figsize=(10, 5))
    plt.title(Figure_Name)
    plot = sns.lineplot(data=data, x=x, y=y)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    for i in plot.containers:
        plot.bar_label(i, )
    plt.subplots_adjust(left=0.3)


def Bar_Plot(data, x, y, Figure_Name, x_label, y_label):
    plt.figure(Figure_Name, figsize=(10, 8))
    plt.title(Figure_Name)
    plot = sns.barplot(data=data, x=x, y=y)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    for i in plot.containers:
        plot.bar_label(i, )
    plot.set_xticklabels(plot.get_xticklabels(), rotation=45)
    plt.subplots_adjust(left=0.3)


def PiePlot(data, title):
    Colors = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
    while re.match("#FFFFFF", Colors[0]):
        Colors.remove(Colors[0])
        Colors = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
    Complementary_Color = Complement_Color(Colors[0])
    Colors.append(Complementary_Color)
    plt.figure(title, figsize=(8, 5))
    plt.title(title)
    plt.pie(data['type'].value_counts(),
            colors=Colors, autopct='%.2f%%')
    plt.legend(labels=data['type'].value_counts().index, loc='lower right', bbox_to_anchor=(1.25, 0))


"""Data Preprocessing"""


def Preprocess_Data(Dataset):
    Number_Of_Empty_Values_Per_Feature = Dataset.isnull().sum()
    print("Number of empty values in each feature: \n", Number_Of_Empty_Values_Per_Feature)
    Number_Of_Total_Empty_Values = Number_Of_Empty_Values_Per_Feature.sum()
    print("Number of empty values in total: \n", Number_Of_Total_Empty_Values)
    Total_Number_Of_Cells = Dataset.shape[0] * Dataset.shape[1]
    Percentage_Of_Missing_Data = (Number_Of_Total_Empty_Values / Total_Number_Of_Cells) * 100
    print("Percentage of missing data: \n", Percentage_Of_Missing_Data)
    for column in Dataset:
        Percentage_Of_Missing_Data_Per_Feature = (Number_Of_Empty_Values_Per_Feature[column] /
                                                  Number_Of_Total_Empty_Values) * 100
        if Percentage_Of_Missing_Data_Per_Feature >= 5:
            Column_Name = '' + column + ''
            Empty_Cell_Value = Column_Name + " " + "Unavailable"
            Dataset[column].fillna(Empty_Cell_Value, inplace=True)
            Column_Name = ''
    Dataset.dropna(how='any', inplace=True)
    print("Checking that there aren't any missing values that haven't been handled: \n", Dataset.isnull().sum())


def Compare_Movies_And_Shows(Dataset):
    PiePlot(Dataset, "Percentage of movies and shows")
    plt.show()


def Top_Ten_Genres_Of_All_Time(Dataset):
    Genres = Dataset.set_index('title').listed_in.str.split(', ', expand=True).stack()
    Genres_Data_Frame = pd.DataFrame()
    Genres_Data_Frame['genre'] = Genres
    Count_Plot(Genres_Data_Frame, 'genre', Genres_Data_Frame.genre.value_counts().iloc[:10].index,
               "Top 10 genres on Netflix", "Number of movies in that genre", "Genre")
    plt.show()
    return Genres_Data_Frame.genre.value_counts().iloc[:10].index


def Frequency_Of_Content_Uploaded_On_Netflix(Dataset):
    Dataset['year_added'] = pd.DatetimeIndex(Dataset['date_added']).year
    Dataset['year_added'].apply(lambda x: int(x))
    Content_Data_Frame = Dataset.year_added.value_counts().to_frame().reset_index()
    Content_Data_Frame.sort_values('year_added', inplace=True)
    Line_Plot(Content_Data_Frame, 'year_added', 'count',
              "Frequency of content uploaded on Netflix", "Year", "Amount of content")
    plt.show()


def Top_Ten_Movies_Or_Shows_Of_All_Time(Dataset):
    Temporary_Data_Frame = Dataset.replace('ratings Unavailable', 0.0)
    Temporary_Data_Frame = Temporary_Data_Frame.nlargest(10, "ratings")
    Bar_Plot(Temporary_Data_Frame, 'title', 'ratings', "Top 10 movies of all time",
             "Movie", "Rating")
    plt.subplots_adjust(bottom=0.3, top=1.0)
    plt.show()


def Top_Ten_Directors_Based_On_Number_Of_Movies_Directed(Dataset):
    Directors = Dataset.set_index('title').director.str.split(', ', expand=True).stack()
    Directors_Data_Frame = pd.DataFrame()
    Directors_Data_Frame['director'] = Directors
    Indices_Of_Unknown_Directors = Directors_Data_Frame[(Directors_Data_Frame['director'] == 'director Unavailable')] \
        .index
    Directors_Data_Frame = Directors_Data_Frame.drop(Indices_Of_Unknown_Directors)
    Count_Plot(Directors_Data_Frame, 'director', Directors_Data_Frame.director.value_counts().iloc[:10].index,
               'Number of movies the directors directed', 'Number of movies', 'Director')
    plt.show()


def Top_Ten_Genres_Over_The_Years(Dataset, Top_Genres):
    List_Of_Top_Genres = list(Top_Genres[:10])
    Genres_And_Their_Data_Frames = dict()
    for Genre in List_Of_Top_Genres:
        Genres_And_Their_Data_Frames[Genre] = Dataset[Dataset['listed_in'] == Genre].year_added.value_counts() \
            .to_frame().reset_index()
    for Genre in Genres_And_Their_Data_Frames:
        Line_Plot(Genres_And_Their_Data_Frames[Genre], 'year_added', 'count',
                  "Top genres over the years", "Year", "Number of movies released in that genre")
    plt.legend(List_Of_Top_Genres)
    plt.show()


def Movies_Per_Year(Dataset):
    Count_Plot(Dataset, 'release_year', Dataset.release_year.value_counts().iloc[:10].index,
               "Number of movies released in each year", "Number of movies", "Year")
    plt.show()


"""Main"""
Netflix_Dataset = pd.read_csv("Netflix Titles.csv")
Preprocess_Data(Netflix_Dataset)
Compare_Movies_And_Shows(Netflix_Dataset)
Top_Genres = Top_Ten_Genres_Of_All_Time(Netflix_Dataset)
Frequency_Of_Content_Uploaded_On_Netflix(Netflix_Dataset)
Top_Ten_Movies_Or_Shows_Of_All_Time(Netflix_Dataset)
Do_Movie_IDs_Already_Exist = Check_Column_Emptiness(Netflix_Dataset, "title_id")
Movie_IDs = Get_Movie_IDs(Netflix_Dataset, Do_Movie_IDs_Already_Exist)
Do_Ratings_Already_Exist = Check_Column_Emptiness(Netflix_Dataset, "ratings")
Ratings_List = Get_Ratings(Netflix_Dataset, Movie_IDs, Do_Ratings_Already_Exist)
Top_Ten_Directors_Based_On_Number_Of_Movies_Directed(Netflix_Dataset)
Top_Ten_Genres_Over_The_Years(Netflix_Dataset, Top_Genres)
Movies_Per_Year(Netflix_Dataset)
