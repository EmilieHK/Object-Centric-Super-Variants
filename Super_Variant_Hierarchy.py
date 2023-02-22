import Super_Variant_Visualization as SVV
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

MODE = SVV.Mode.LANE_FREQUENCY
TOOLTIPS = True

def explore_hierarchy_bottom_up(super_variants):
    '''
    Visualizes the layera of a generated Super Variant hierarchy, allowing the navigation among Super Variants within a layer and between the layers.
    :param super_variants: The Super Variant hierarchy with a key-value pair for each layer of the hierarchy. The key indicates the layer index
    :type super_variants: dict
    '''
    layers = []
    for i in range(len(list(super_variants.keys()))):
        layers.append([super_variant[0] for super_variant in super_variants[i][0]])

    visualize_super_variant_layer(layers, 0, 0)

def explore_hierarchy_top_down(final_super_variant):
    '''
    Visualizes a Super Variant and its two direct predecessors in the generation, allowing to navigate the Super Variants top-down from this starting point.
    :param final_super_variant: The starting Super Variant and its unterlying direct predecessors
    :type final_super_variant: tuple
    '''
    if(final_super_variant[1] == None and final_super_variant[2] == None):
        SVV.visualize_super_variant(final_super_variant[0])
    else:
        visualize_single_summarization_step(final_super_variant[1], final_super_variant[2], final_super_variant[0])


def visualize_super_variant_layer(super_variants, current_layer, current_start_index):
    '''
    Visualizes up to 3 Super Variants in a single layer of a generated Super Variant hierarchy, allowing the navigation among Super Variants within a layer and between the layers.
    :param super_variants: The Super Variant hierarchy with a key-value pair for each layer of the hierarchy. The key indicates the layer index
    :type super_variants: dict
    :param current_layer: The index of the layer currently visualized
    :type current_layer: int
    :param current_start_index: The index of the first Super Variant in the current layer that is to be visualized
    :type current_start_index: int
    '''
    current_layer = max(0, current_layer)
    current_layer = min(len(super_variants)-1, current_layer)
    current_super_variants = super_variants[current_layer]

    maximal_index = len(current_super_variants)
    start_index = current_start_index % maximal_index
    end_index = (current_start_index + 3) % maximal_index

    if(maximal_index <= 3):
        visible_super_variants = current_super_variants

    elif(end_index > start_index):
        visible_super_variants = current_super_variants[start_index: end_index]

    else: 
        visible_super_variants = current_super_variants[start_index:] + current_super_variants[:end_index]

    number_of_plots = min(3, len(visible_super_variants))
    current_annotations = []

    if(number_of_plots > 1):
        fig, ax = plt.subplots(1, number_of_plots, figsize=(20,10), sharey = True) 
        ax = list(ax)

        for i in range(number_of_plots):

            length = visible_super_variants[i].get_length()
            ax[i], width, height = SVV.arrange_super_variant(visible_super_variants[i], ax[i], 0, 0, "*", SVV.Mode.NO_FREQUENCY, 4.5 * 3 / number_of_plots, 4.5 * 3 / number_of_plots, int((13 * 9 / length)))
        
            ax[i].set_xlim(-15, width + 2)
            ax[i].set_ylim(-2, height + 2)

            ax[i].set_aspect('equal')
            ax[i].axis('off')

            if(TOOLTIPS):
                current_annotations.append(ax[i].annotate("See Super Variant " + str(visible_super_variants[i].id) + " in Detail", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                        bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
                ax[i].figure.texts.append(ax[i].texts.pop())


        ax = tuple(ax)
        fig.subplots_adjust(wspace=0.03, hspace=0)
    
    else:
        fig, ax = plt.subplots()
        if(MODE == SVV.Mode.LANE_FREQUENCY):
            mode = SVV.Mode.ACTIVITY_FREQUENCY
        else:
            mode = MODE
        ax, width, height = SVV.arrange_super_variant(visible_super_variants[0], ax, 0, 0, "*", mode, 9, 9, 13)
        ax.set_aspect('equal')
        ax.set_xlim(-20, width + 2)
        ax.set_ylim(-2, height + 2)
        plt.axis('off')


    def hover_info(event):
        if(number_of_plots > 1):
            for i in range(number_of_plots):
                annotate = current_annotations[i]
                annotation_visbility = annotate.get_visible()
                if event.inaxes == ax[i]:
                                
                    event_position = (round(event.xdata), round(event.ydata))
                    annotate.xy = event_position
                    annotate.set_visible(True)
                    fig.canvas.draw_idle()

                elif(annotation_visbility):
                    annotate.set_visible(False)
                    fig.canvas.draw_idle()


    def click(event):
        if(number_of_plots > 1):
            for i in range(number_of_plots):
                if event.inaxes == ax[i]:
                    SVV.visualize_super_variant(visible_super_variants[i], mode = MODE)


    def go_left_right(event):

        if(event.key == '"left"'):
            if(len(current_super_variants) > 3):
                visualize_super_variant_layer(super_variants, current_layer, current_start_index - 1)
                plt.close(fig)

        elif(event.key == 'right'):
            if(len(current_super_variants) > 3):
                visualize_super_variant_layer(super_variants, current_layer, current_start_index + 1)
                plt.close(fig)

        elif(event.key == 'up'):
            if(current_layer < len(super_variants)-1):
                visualize_super_variant_layer(super_variants, current_layer + 1, 0)
                plt.close(fig)

        elif(event.key == 'down'):
            if(current_layer > 0):
                visualize_super_variant_layer(super_variants, current_layer - 1, 0)
                plt.close(fig)
                

    if(TOOLTIPS):                     
        fig.canvas.mpl_connect('motion_notify_event', hover_info)
    fig.canvas.mpl_connect('button_press_event', click)
    fig.canvas.mpl_connect('key_press_event', go_left_right)

    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.show()

    fig.savefig("SuperVariantsLayer/Layer_" + str(current_layer) + "_" + str(start_index) + "_to_" + str((current_start_index + 2) % maximal_index) + ".svg")


def visualize_single_summarization_step(super_variant_1, super_variant_2, new_super_variant):
    '''
    Visualizes up to 3 Super Variants in a single layer of a generated Super Variant hierarchy, allowing the navigation among Super Variants within a layer and between the layers.
    :param super_variant_1: One of the direct predecessors of the given Super Variant
    :type super_variant_1: tuple
    :param super_variant_2: The other direct predecessors of the given Super Variant
    :type super_variant_2: tuple
    :param new_super_variant: The Super Variant as a result of the other given two Super Variants
    :type new_super_variant: tuple
    '''

    if(MODE == SVV.Mode.LANE_FREQUENCY):
        mode = SVV.Mode.ACTIVITY_FREQUENCY
    else:
        mode = MODE

    fig = plt.figure(figsize=(8,2))
    current_annotations = []

    gs = fig.add_gridspec(2,2)
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])
    ax3 = fig.add_subplot(gs[0, :])


    length1 = super_variant_1[0].get_length()
    ax1, width1, height1 = SVV.arrange_super_variant(super_variant_1[0], ax1, 0, 0, "*", mode, 7, 7, int(9 * 13 / length1))
    
    ax1.set_aspect('equal')
    ax1.set_xlim(-15, width1 + 2)
    ax1.set_ylim(-2, height1 + 2)
    ax1.axis('off')

    if(TOOLTIPS):
        if(super_variant_1[1] != None and super_variant_1[2] != None):
            current_annotations.append(ax1.annotate("See Details on this Super Variants Summarization", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                        bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        else:
            current_annotations.append(ax1.annotate("See Super Variant " + str(super_variant_1[0].id) + " in Detail", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                        bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        
        ax1.figure.texts.append(ax1.texts.pop())

    length2 = super_variant_2[0].get_length()
    ax2, width2, height2 = SVV.arrange_super_variant(super_variant_2[0], ax2, 0, 0, "*", mode, 7, 7, int(9 * 13 / length2))
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-15, width2 + 2)
    ax2.set_ylim(-2, height2 + 2)
    ax2.axis('off')

    if(TOOLTIPS):
        if(super_variant_2[1] != None and super_variant_2[2] != None):
            current_annotations.append(ax2.annotate("See Details on this Super Variants Summarization", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                        bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        else:
            current_annotations.append(ax2.annotate("See Super Variant " + str(super_variant_2[0].id) + " in Detail", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                        bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        
        ax2.figure.texts.append(ax2.texts.pop())

    ax3, width3, height3 = SVV.arrange_super_variant(new_super_variant, ax3, 0, 0, "*", mode, 9, 9, 13)
    
    ax3.set_aspect('equal')
    ax3.set_xlim(-15, width3 + 2)
    ax3.set_ylim(-2, height3 + 2)
    ax3.axis('off')

    if(TOOLTIPS):
        current_annotations.append(ax3.annotate("See Super Variant " + str(new_super_variant.id) + " in Detail", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                        bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        
        ax3.figure.texts.append(ax3.texts.pop())

    def hover_info(event):

        annotate = current_annotations[0]
        annotation_visbility = annotate.get_visible()
        if event.inaxes == ax1:
                            
            event_position = (round(event.xdata), round(event.ydata))
            annotate.xy = event_position
            annotate.set_visible(True)
            fig.canvas.draw_idle()

        elif(annotation_visbility):
            annotate.set_visible(False)
            fig.canvas.draw_idle()

        annotate = current_annotations[1]
        annotation_visbility = annotate.get_visible()
        if event.inaxes == ax2:
                            
            event_position = (round(event.xdata), round(event.ydata))
            annotate.xy = event_position
            annotate.set_visible(True)
            fig.canvas.draw_idle()

        elif(annotation_visbility):
            annotate.set_visible(False)
            fig.canvas.draw_idle()

        annotate = current_annotations[2]
        annotation_visbility = annotate.get_visible()
        if event.inaxes == ax3:
                            
            event_position = (round(event.xdata), round(event.ydata))
            annotate.xy = event_position
            annotate.set_visible(True)
            fig.canvas.draw_idle()

        elif(annotation_visbility):
            annotate.set_visible(False)
            fig.canvas.draw_idle()

    def click(event):

        if event.inaxes == ax1:
            if(super_variant_1[1] != None and super_variant_1[2] != None):
                visualize_single_summarization_step(super_variant_1[1], super_variant_1[2], super_variant_1[0])

            else:
                SVV.visualize_super_variant(super_variant_1[0], mode = MODE)

        elif event.inaxes == ax2:
            if(super_variant_2[1] != None and super_variant_2[2] != None):
                visualize_single_summarization_step(super_variant_2[1], super_variant_2[2], super_variant_2[0])

            else:
                SVV.visualize_super_variant(super_variant_2[0], mode = MODE)

        elif event.inaxes == ax3:
            SVV.visualize_super_variant(new_super_variant, mode = MODE)


    fig.subplots_adjust(wspace=0.03, hspace=0)

    if(TOOLTIPS):
        fig.canvas.mpl_connect('motion_notify_event', hover_info)
    fig.canvas.mpl_connect('button_press_event', click)

    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.show()

    fig.savefig("SuperVariantCompositions/SuperVariant_" + str(new_super_variant.id) + "_from" + str(super_variant_1[0].id) + "_and_" + str(super_variant_2[0].id) + ".svg")