'''
Created on 4 kwi 2022

@author: spasz
'''
import os
import cv2
import pandas as pd
from helpers.textAnnotations import ReadAnnotations, GetImageFilepath
from helpers.boxes import ToAbsolute, ExtractBoxImagePart
from helpers.MarkdownReport import MarkdownReport
from helpers.files import CreateDirectory, FixPath, GetFilename


class DecoratorDistributionShowcase:
    '''
    classdocs
    '''

    def __init__(self,
                 subdirectory=''):
        '''
        Constructor
        '''
        # Subdirectory
        self.subdirectory = subdirectory
        # Base directory of dataframe files
        self.directory = ''

        # Thresholds
        # -------------------
        # Number of selected items
        self.categoryItems = 9

    def GetCategoriesAnnotations(self, df):
        ''' Select images for all categories.'''
        # Dictionary with selected images for categories
        results = {}
        # Iterate over all column category except file and directory
        categories = set(df.columns) - {'Directory', 'File', 'Width', 'Height'}
        for category in categories:
            # Select df part with this category values == 1
            subdf = df.loc[(df[category] == 1) & (df['Width'] >= df['Width'].median()) & (
                df['Height'] >= df['Height'].median())]
            # Select first nine items/annotations
            items = []
            for index, row in subdf.iterrows():
                # Create annotation path
                annotationPath = row['Directory'] + row['File']
                # Get image path and read image
                imgPath = GetImageFilepath(annotationPath)
                if (os.path.exists(imgPath)):
                    # Add item if validated.
                    items.append(row['Directory']+row['File'])
                    # Finish when enough
                    if (len(items) == self.categoryItems):
                        break

            # Store in results
            results[category] = items

        return results

    def GetCategoriesSubimages(self, categoriesAnnotations):
        ''' Convert to subimages of categories annotations'''
        # Results dictionary
        results = {}
        # For each category generate subimages of category items
        for category in categoriesAnnotations.keys():
            # List of created category images
            categoryImages = []
            # For each annotation path
            for i, annotationPath in enumerate(categoriesAnnotations[category]):
                # Get image path and read image
                imgPath = GetImageFilepath(annotationPath)
                if (os.path.exists(imgPath)):
                    image = cv2.imread(imgPath)
                    # Read annotations & convert to absolute pixel positions
                    annotations = ReadAnnotations(imgPath)
                    # Find current 'category annotation'
                    for classNumber, box in annotations:
                        if (classNumber == category):
                            # Recalculate to absolute pix position
                            box = ToAbsolute(
                                box, image.shape[1], image.shape[0])
                            # Extract sub image
                            subimage = ExtractBoxImagePart(image, box)
                            # Save as extra image
                            outpath = self.directory+self.subdirectory + \
                                str(category)+'_'+str(i)+'.png'
                            cv2.imwrite(outpath, subimage)
                            # Store
                            categoryImages.append(outpath)
                            break

            # Add to results
            results[category] = categoryImages

        return results

    def CreateCategoryHistogram(self, category, categoryDf):
        ''' Creates histogram based on category df.'''
        histPath = self.directory + self.subdirectory + \
            'Category%uHistogram.png' % category
        histogramDf = categoryDf[['Width', 'Height']]
        hist = histogramDf.plot.hist(bins=16, stacked=False, figsize=(16, 8))
        fig = hist.get_figure()
        fig.savefig(histPath)
        return histPath

    def CreateSummaryHistogram(self, summaryDf):
        ''' Creates histogram based on summary df.'''
        histPath = self.directory + self.subdirectory + 'SummaryHistogram.png'
        histogramDf = summaryDf[['Annotations']]
        hist = histogramDf.plot.bar(y='Annotations')
        fig = hist.get_figure()
        fig.savefig(histPath)
        return histPath

    def CreateShowcaseReport(self, categoriesImages, df):
        ''' Convert to subimages of categories annotations'''
        # Get global informations
        totalAnnotations = len(df)
        totalImages = len(df['File'].unique())
        categoriesSummary = {
            'Index': [],
            'Annotations': [],
            'Images': [],
            'Bbox width': [],
            'Bbox height': [],
        }
        # Always remove previous Showcase
        showcasePath = self.directory+self.subdirectory+'Showcase.md'
        os.remove(showcasePath)

        # Start report
        report = MarkdownReport(filepath=showcasePath)
        report.Begin(title='Distribution showcase')

        # For each category generate subimages of category items
        for category in sorted(categoriesImages.keys()):
            # Calculate category parameters
            categoryDf = df.loc[df[category] == 1]
            categoryAnnotations = len(categoryDf)
            categoryImages = len(categoryDf['File'].unique())
            categoryMeanWidth = categoryDf['Width'].mean()
            categoryMeanHeight = categoryDf['Height'].mean()
            # Create histogram of category data
            histPath = self.CreateCategoryHistogram(category, categoryDf)
            # Append data to summary
            categoriesSummary['Index'].append(category)
            categoriesSummary['Annotations'].append(
                100*categoryAnnotations/totalAnnotations)
            categoriesSummary['Images'].append(100*categoryImages/totalImages)
            categoriesSummary['Bbox width'].append(categoryMeanWidth)
            categoriesSummary['Bbox height'].append(categoryMeanHeight)
            # Start section
            report.AddSection(text='Category %s' % str(category))
            report.AddText('Category images %u/%u (%2.2f%%).\n' %
                           (categoryImages, totalImages, categoryImages*100/totalImages))
            report.AddText('Category annotations %u/%u (%2.2f%%).\n' % (
                categoryAnnotations, totalAnnotations, categoryAnnotations*100/totalAnnotations))
            report.AddText('Category Bbox mean width %2.2f.\n' %
                           (categoryMeanWidth))
            report.AddText('Category Bbox mean height %2.2f.\n' %
                           (categoryMeanHeight))
            report.AddImage(histPath)
            # Add also each category image
            for imagepath in categoriesImages[category]:
                report.AddImage(imagepath)
            # Finish section
            report.AddLineSeparator()

        # Add summary of categories
        categoriesSummaryDf = pd.DataFrame.from_dict(categoriesSummary)
        categoriesSummaryDf.set_index('Index', inplace=True)
        summaryImgPath = self.CreateSummaryHistogram(categoriesSummaryDf)
        report.AddSection('Categories summary')
        report.AddImage(summaryImgPath)
        report.AddDataframe(categoriesSummaryDf)
        report.End()

    def Decorate(self, df):
        ''' Decorate dataframe.'''
        # Get base directory
        self.directory = df['Directory'].iat[0]
        # Create subdirectory if needed
        if (len(self.subdirectory) != 0):
            self.subdirectory = FixPath(self.subdirectory)
            CreateDirectory(self.directory+self.subdirectory)

        # Select categories annotations
        categoriesAnnotations = self.GetCategoriesAnnotations(df)
        # Create subimages from annotations
        categoriesImages = self.GetCategoriesSubimages(categoriesAnnotations)
        # Create showcase .md
        self.CreateShowcaseReport(categoriesImages, df)

        return None
