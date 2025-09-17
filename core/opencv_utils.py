import cv2
import numpy as np
import math
from utils import *
from mapmask import MapMask

from scipy.spatial import ConvexHull, convex_hull_plot_2d

# =====
# Erosion and dilation operations
# =====

def openSection (src: cv2.Mat, erosion_size: int, ite: int) -> cv2.Mat:
    """
    Apply erosion then dilation on the source image.
    Return the resulting image.
    """

    erosion_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dilation_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dst: cv2.Mat = src.copy()

    for i in range(ite):
        dst = cv2.erode(dst, erosion_kernel)

    for i in range(ite):
        dst = cv2.dilate(dst, dilation_kernel)

    return dst


def closeSection (src: cv2.Mat, erosion_size: int, ite: int) -> cv2.Mat:
    """
    Apply dilation then erosion on the source image.
    Return the resulting image.
    """

    erosion_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dilation_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dst: cv2.Mat = src.copy()

    for i in range(ite):
        dst = cv2.dilate(dst, dilation_kernel)

    for i in range(ite):
        dst = cv2.erode(dst, erosion_kernel)

    return dst



def getCenterOfSection(section :cv2.Mat) -> Point:
    """
    Compute the centroid of all points of a section.
    """

    y, x = np.where(section > 0)
    count :int = len(x)

    centroid = Point(int(np.sum(x)/count), int(np.sum(y)/count))

    return centroid


def getNearestPoint (p: Point, vec: np.ndarray):

    nearestPoint = PointB(r=9999)

    for pv in vec:

        if (pv == p):
            return p

        r = cv2.norm(np.array([p.x - pv.x, p.y - pv.y]))
        if (r < nearestPoint.r):
            nearestPoint.x = pv.x
            nearestPoint.y = pv.y
            nearestPoint.r = r

    return Point(nearestPoint.x, nearestPoint.y)



def testICH():
    src = cv2.imread("/home/patobeur/Documents/GitHub/BoneMap/tests/sec_170.png", cv2.IMREAD_GRAYSCALE)
    dst: cv2.Mat = src.copy()

    fillValue = 128
    hullValue = 125

    contours, hierarchy = cv2.findContours(src, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contour = np.array([p.flatten() for p in contours[0]])

    hull = ConvexHull(contour)
    hull_points = np.array([contour[i] for i in hull.vertices])

    cv2.drawContours(dst, [hull_points], -1, (hullValue, hullValue, hullValue), 1)
    centroid = getCenterOfSection(src)

    h,w = dst.shape
    innerShape = np.zeros((h+2,w+2),np.uint8)
    
    floodflags = 4
    floodflags |= cv2.FLOODFILL_MASK_ONLY
    floodflags |= (fillValue << 8)

    cv2.floodFill(dst, innerShape, (centroid.x, centroid.y), (fillValue,fillValue,fillValue), (10,)*3, (10,)*3, floodflags)

    cv2.imshow('convex hull', innerShape)
    if cv2.waitKey(0):
        cv2.destroyAllWindows()

    openedSection = openSection(innerShape, 15, 2)

    cv2.imshow('convex hull', openedSection)
    if cv2.waitKey(0):
        cv2.destroyAllWindows()








#void Process::testICH() {

#    Mat src = imread("C:/Users/Patobeur/Documents/Qt Projects/BoneMap/F87_FemR/BoneGeom/sec_170.png", IMREAD_GRAYSCALE);
#    Mat dst;
#    src.copyTo(dst);

#    uint fillValue = 128;
#    uint hullValue = 125;

#    vector<vector<Point> > contours;
#    findContours( src, contours, RETR_TREE, CHAIN_APPROX_SIMPLE );

#    vector<vector<Point> >hull( contours.size() );
#    convexHull( contours[0], hull[0] );
#
#    Scalar color = Scalar( rng.uniform(0, 256), rng.uniform(0,256), rng.uniform(0,256) );
#    Scalar fillColor = Scalar( fillValue, fillValue, fillValue );

#    Mat sectionHull = Mat::zeros(src.size(), src.type());
#    drawContours(sectionHull, hull, 0, Scalar(255,255,255));
#    Point centroid = getCenterOfSection(sectionHull);
#    floodFill(sectionHull, centroid, Scalar(255, 255, 255), 0, cv::Scalar(), cv::Scalar(), 4);

#    vector<vector<Point> > hullContours;
#    findContours( sectionHull, hullContours, RETR_TREE, CHAIN_APPROX_SIMPLE );

#    for (uint i = 0; i < hullContours[0].size(); ++i) {
#        Point nearestPoint = getNearestPoint(hullContours[0].at(i), contours[0]);
#        hullContours[0].at(i).x = nearestPoint.x;
#        hullContours[0].at(i).y = nearestPoint.y;
#    }

#    drawContours(dst, hullContours, 0, Scalar(255,255,255));
#    floodFill(dst, centroid, Scalar(fillValue, fillValue, fillValue), 0, cv::Scalar(), cv::Scalar(), 4);
#
#    Mat innerShape = Mat::zeros(src.size(), src.type());
#
#    for (uint i = 0; i < dst.size().height; ++i)
#    {
#        for (uint j = 0; j < dst.size().width; ++j)
#        {
#            if (dst.at<unsigned char>(i, j) == fillValue)
#            {
#                innerShape.at<unsigned char>(i, j) = 255;
#            }
#        }
#    }
#
#    open(innerShape, &innerShape, 15);
#
#    vector<vector<Point> > innerContour;
#    findContours( innerShape, innerContour, RETR_TREE, CHAIN_APPROX_SIMPLE );
#
#    for (uint i = 0; i < innerContour[0].size(); ++i) {
#        Point nearestPoint = getNearestPoint(innerContour[0].at(i), contours[0]);
#        innerContour[0].at(i).x = nearestPoint.x;
#        innerContour[0].at(i).y = nearestPoint.y;
#    }
#
#    drawContours(dst, innerContour, 0, Scalar(255,255,255));
#
#    Mat final;
#    src.copyTo(final);
#    drawContours(final, hullContours, 0, Scalar(255,255,255));
#    drawContours(final, innerContour, 0, fillColor);
#
#    floodFill(final, Point(600,480), Scalar(255, 255, 255), 0, cv::Scalar(), cv::Scalar(), 4);
#
#    for (uint i = 0; i < final.size().height; ++i)
#    {
#        for (uint j = 0; j < final.size().width; ++j)
#        {
#            if (final.at<unsigned char>(i, j) == fillValue)
#            {
#                final.at<unsigned char>(i, j) = 0;
#            }
#        }
#    }
#
#    close(final, &final, 15);
#
#
#    imshow("result", final);
#
#}