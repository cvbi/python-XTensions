# XTension to create plots from density based cell clustering
#
#  Copyright (C) 2018 Nilesh patil <nilesh.patil@rochester.edu>, MIT license
#
#    <CustomTools>
#      <Menu name = "Python plugins">
#       <Submenu name = "Plots">
#        <Item name="Create 3D plot from density model for cells" icon="Python" tooltip="">
#         <Command>PythonXT::XT_cluster_plot_cells(%i)</Command>
#        </Item>
#       </Submenu>
#      </Menu>
#    </CustomTools>

import os
import time
from itertools import cycle
from mpl_toolkits.mplot3d import axes3d

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import kneighbors_graph

import ImarisLib
from cvbi.base_imaris.stats import *
from cvbi.gui import *


def XT_cluster_plot_cells(aImarisId) :
    vImarisLib = ImarisLib.ImarisLib( )
    vImaris = vImarisLib.GetApplication( aImarisId )
    vDataSet = vImaris.GetDataSet( )

    imaris_file = vImaris.GetCurrentFileName( )
    imaris_dir = os.path.dirname( imaris_file )
    imaris_name = os.path.basename( imaris_file )

    print('''
    ##################################
    ####### XTension Started #########
    ##################################
    ''')
    time.sleep( 5 )

    nT = vDataSet.GetSizeT( )

    cX_min = vDataSet.GetExtendMinX( )
    cY_min = vDataSet.GetExtendMinY( )
    cZ_min = vDataSet.GetExtendMinZ( )

    cX_max = vDataSet.GetExtendMaxX( )
    cY_max = vDataSet.GetExtendMaxY( )
    cZ_max = vDataSet.GetExtendMaxZ( )

    object_type_list = ["surfaces" , "spots" , "cells"]
    object_type = create_window_from_list( object_list = object_type_list ,
                                           window_title = 'Select one object type.' ,
                                           w = 500 , h = 50 * len( object_type_list ) )
    print('Object type Selected : ' + object_type)
    time.sleep( 1 )

    objects = GetSurpassObjects( vImaris = vImaris , search = object_type )
    objects_list = objects.keys( )
    object_selected = create_window_from_list( object_list = objects_list ,
                                               window_title = 'Select Imaris object to plot.' ,
                                               w = 500 , h = 50 * len( objects_list ) )
    print('Object Selected : ' + object_selected)
    time.sleep( 1 )

    output_dir = get_dir( window_title = 'Select output directory.' , initial_dir = imaris_dir )

    print('\nGetting statistics from Imaris for {o}\n'.format( o = object_selected ))
    time.sleep( 1 )

    data = get_imaris_statistics( vImaris = vImaris , object_type = object_type , object_name = object_selected )
    columns_use = ['trackID' , 'Time Index' , 'Position X' , 'Position Y' , 'Position Z']
    data_tn = data.loc[: , columns_use]
    data_tn.columns = ['trackID' , 'time' , 'x' , 'y' , 'z']

    print('Data loaded.')
    time.sleep( 3 )


    t_selected = 1
    if nT > 1:
        t_selected = create_window_for_input(default=t_selected,
                                            w=400, h=500,
                                            window_title='Select time to cluster at.',
                                            window_text='Provide an integer time point for clustering.',
                                            valid_range=[1, nT])
    t_selected = np.int64(t_selected)
    time.sleep(2)

    print('Plotting started.\n')
    time.sleep( 3 )

    ti = t_selected
    data_ti = data_tn.loc[data_tn.time == ti , :]
    data_in = data_ti.loc[: , ['x' , 'y' , 'z']]
    X = data_in.values


    # Create All distance hyperbole plots
    print('\nPlotting All distances.')
    path_plot_out = output_dir + '/k_vs_distanceAll_{o}.png'.format( o = object_selected )
    plt.figure( figsize = (10 , 10) , dpi = 500 )
    for k in [1 , 2 , 3 , 5 , 10 , 15 , 20 , 25] :
        X_knn = kneighbors_graph( X = X , n_neighbors = k , mode = 'distance' , include_self = False )
        distances = np.triu( m = X_knn.toarray( ) )

        super_title = 'Selecting distance criterion based on sorted distance vs nCells hyperbola from nearest neighbours'
        line_01 = str( k ) + ' Nearest Neighbours'

        plt.plot( np.sort( distances[distances > 0] ) , ls = '-.' , lw = 1.5 , alpha = 0.9 , label = line_01 )

        plt.ylim( 0 , 150 )
        plt.xlabel( 'n (neighbours)')
        plt.ylabel( 'D (in $\mu$m)' )
        plt.title( super_title );
    plt.legend( loc = 'lower right' );
    plt.savefig( path_plot_out , dpi = 250 );
    time.sleep( 3 )


    # Create Maximum distance hyperbole plots

    path_plot_out = output_dir + '/k_vs_distanceMax_{o}.png'.format( o = object_selected )
    plt.figure( figsize = (10 , 6) , dpi = 500 )
    for k in [1 , 2 , 3 , 5 , 10 , 15 , 20 , 25] :
        X_knn = kneighbors_graph( X = X , n_neighbors = k , mode = 'distance' , include_self = False )
        distances = np.triu( m = X_knn.toarray( ) )

        super_title = 'Selecting distance criterion based on sorted distance vs nCells hyperbola from nearest neighbours'
        line_02 = 'Maximum of ' + str( k ) + ' Nearest Neighbours'

        plt.plot( np.sort( distances.max( -1 ) ) , ls = '--' , lw = 1.5 , alpha = 0.9 , label = line_02 )

        plt.ylim( 0 , 350 )
        plt.xlabel( 'n (neighbours)' )
        plt.ylabel( 'D (in $\mu$m)' )
        plt.title( super_title );
    plt.legend( loc = 'upper left' );
    plt.savefig( path_plot_out , dpi = 250 );
    time.sleep( 3 )


    # Create cluster plots

    k = 10
    ti = t_selected
    Ns = [2 , 3 , 5 , 10 , 15]
    Rs = [10 , 20 , 50 , 75]
    time.sleep(2)

    data_ti = data_tn.loc[data_tn.time == ti , :]
    data_in = data_ti.loc[: , ['x' , 'y' , 'z']]
    X = data_in.values

    x = data_ti.x
    y = data_ti.y
    z = data_ti.z
    print('\nCreating 3D plots :\n')
    print(axes3d)

    for r in Rs :

        path_plot_out = output_dir + '/density_driven_clusters_R{r}_{o}.png'.format(r = str(r), o = object_selected)
        matplotlib.rcParams.update( { 'font.size' : 6 } )
        fig = plt.figure( figsize = (18 , 12) , dpi = 500 )

        i = 1
        for n in Ns :

            clusterer = DBSCAN( eps = r , min_samples = n )
            clusterer.fit(X)
            labels = clusterer.labels_
            unique_labels = np.unique( ar = labels , return_counts = True )
            spectrum = plt.cm.get_cmap('Spectral')
            colors = [spectrum( each ) for each in np.linspace( 0 , 1 , len(unique_labels[0] ) )]

            clusters = pd.DataFrame.from_records( data = unique_labels , index = ['cluster' , 'nCells'] ).T
            try:
                clusters = clusters.loc[clusters.cluster>-1,:].copy()
            except:
                pass

            nCluster = (clusters.nCells >= k).sum( )
            nRegions = clusters.shape[0]

            subset = labels >= -1
            ax = fig.add_subplot( 3 , len( Ns ) , i , projection = '3d' )
            ax.grid( False );
            ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False

            ax.scatter3D( x[subset] , y[subset] , z[subset] ,
                          c = [colors[label+1] for label in labels[subset]] ,
                          alpha = 0.75 , lw = 0 , s = 5 );

            ax.set_xlim3d( cX_min , cX_max )
            ax.set_ylim3d( cY_min , cY_max )
            ax.set_zlim3d( cZ_min , cZ_max )
            ax.view_init( elev = 75 , azim = -90 );

            ax.set_title( ('R :' + str( r ) +
                           ', N :' + str( n ) +
                           ', nRegions :' + str( nRegions ) +
                           ', nClusters :' + str( nCluster ) +
                           ''
                           ) )
            if i == 1 :
                ax.annotate( 'All cells' , xy = (-0.0001 , 0.5) , xycoords = 'axes fraction' );

            subset = labels > -1
            ax = fig.add_subplot( 3 , len( Ns ) , i + 1 * len( Ns ) , projection = '3d' )
            ax.grid( False );
            ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
            ax.scatter3D( x[subset] , y[subset] , z[subset] ,
                          c = [colors[label+1] for label in labels[subset]] ,
                          alpha = 0.75 , lw = 0 , s = 5 );

            ax.set_xlim3d( cX_min , cX_max )
            ax.set_ylim3d( cY_min , cY_max )
            ax.set_zlim3d( cZ_min , cZ_max )
            ax.view_init( elev = 75 , azim = -90 );

            if i == 1 :
                ax.annotate( 'Dense Regions' , xy = (-0.0001 , 0.5) , xycoords = 'axes fraction' );

            subset = (labels > -1) & [(labels == l).sum( ) >= k for l in labels]
            ax = fig.add_subplot( 3 , len( Ns ) , i + 2 * len( Ns ) , projection = '3d' )
            ax.grid( False );
            ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
            ax.scatter3D( x[subset] , y[subset] , z[subset] ,
                          c = [colors[label+1] for label in labels[subset]] ,
                          alpha = 0.75 , lw = 0 , s = 5 );

            ax.set_xlim3d( cX_min , cX_max )
            ax.set_ylim3d( cY_min , cY_max )
            ax.set_zlim3d( cZ_min , cZ_max )
            ax.view_init( elev = 75 , azim = -90 );

            if i == 1 :
                ax.annotate( 'Clusters (k>=' + str( k ) + ')' , xy = (-0.0001 , 0.5) , xycoords = 'axes fraction' );

            i += 1

        fig.subplots_adjust( hspace = 0.01 , wspace = 0.01 );
        plt.savefig(path_plot_out , dpi = 500 )
        plt.close()

    print('''
    ############################################
    #####          XTension Finished       #####
    #####   Wait 5s to Close automatically #####
    ############################################
    ''')
    time.sleep( 5 )
