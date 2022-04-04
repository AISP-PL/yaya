'''
Created on 4 kwi 2022

@author: spasz
'''
import os
import cv2
from helpers.textAnnotations import ReadAnnotations, GetImageFilepath
from helpers.boxes import ToAbsolute, ExtractBoxImagePart


class DecoratorDistributionShowcase:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # Number of selected items
        self.categoryItems = 9

    def GetCategoriesAnnotations(self, df):
        ''' Select images for all categories.'''
        # Dictionary with selected images for categories
        results = {}
        # Iterate over all column category except file and directory
        categories = set(df.columns) - {'Directory', 'File'}
        for category in categories:
            # Select df part with this category values == 1
            subdf = df.loc[df[category] == 1]
            # Select first nine items/annotations
            items = []
            for index, row in subdf.iterrows():
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
            for annotationPath in categoriesAnnotations[category]:
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
                            outpath = imgPath+'.part.png'
                            cv2.imwrite(outpath, subimage)
                            # Store
                            categoryImages.append(outpath)
                            break

            # Add to results
            results[category] = categoryImages

        return results

    def Decorate(self, df):
        ''' Decorate dataframe.'''
        # Select categories annotations
        categoriesAnnotations = self.GetCategoriesAnnotations(df)
        # Create subimages from annotations
        categoriesImages = self.GetCategoriesSubimages(categoriesAnnotations)
        # Create showcase .md

        return None
