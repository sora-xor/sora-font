#!/usr/bin/env python

'''
Current draft for modernized mark feature writer module.
This work is incomplete (i.e. support for Indic mark features still
needs to be added).
The anchor_name_no_underscore process is odd and was added to patch a bug.
'''

import os
import sys
import argparse
from defcon import Font

default_mark_file = 'mark.fea'
default_mkmk_file = 'mkmk.fea'
default_mkclass_file = 'markclasses.fea'
default_abvm_file = 'abvm.fea'
default_blwm_file = 'blwm.fea'
default_mkgrp_name = 'COMBINING_MARKS'

default_trim_tags = False
default_indic_format = False
default_write_mkmk = False
default_write_classes = False


def write_output(directory, file, data):
    f_path = os.path.join(directory, file)
    with open(f_path, 'w') as of:
        of.write(data)
    print('writing {}'.format(file))


def trim_anchor_name(anchor_name):
    suffixes = ['UC', 'LC', 'SC']
    for suffix in suffixes:
        if anchor_name.endswith(suffix):
            trimmed_name = anchor_name.replace(suffix, '')
            return trimmed_name
    return anchor_name


class AnchorMate(object):
    '''
    AnchorMate lifts anchors from one or more glyphs and
    sorts them in a dictionary {a_position: gName}
    '''

    def __init__(self, anchor):
        self.pos_name_dict = {}


class run(object):
    def __init__(
        self,
        input_file,
        mark_file=default_mark_file,
        mkmk_file=default_mkmk_file,
        mkclass_file=default_mkclass_file,
        abvm_file=default_abvm_file,
        blwm_file=default_blwm_file,
        mkgrp_name=default_mkgrp_name,
        trim_tags=default_trim_tags,
        indic_format=default_indic_format,
        write_mkmk=default_write_mkmk,
        write_classes=default_write_classes,
    ):

        self.mark_file = mark_file
        self.mkmk_file = mkmk_file
        self.mkclass_file = mkclass_file
        self.abvm_file = abvm_file
        self.blwm_file = blwm_file
        self.mkgrp_name = mkgrp_name
        self.trim_tags = trim_tags
        self.indic_format = indic_format
        self.write_mkmk = write_mkmk
        self.write_classes = write_classes

        ufo_path = input_file
        ufo_dir = os.path.dirname(
            os.path.normpath(ufo_path)
        )
        print(os.path.dirname(ufo_path))
        f = Font(ufo_path)
        self.glyph_order = f.lib['public.glyphOrder']

        combining_anchor_dict = {}
        combining_marks_group = f.groups.get(self.mkgrp_name, [])
        if not combining_marks_group:
            print(
                'No group named "{}" found. '
                'Please add it to your UFO file '
                '(and combining marks to it).'.format(self.mkgrp_name)
            )
            sys.exit()

        combining_marks = [f[g_name] for g_name in combining_marks_group]

        mkmk_anchor_dict = {}
        mkmk_marks = [g for g in combining_marks if not all(
            [anchor.name.startswith('_') for anchor in g.anchors])]

        base_glyph_anchor_dict = {}
        base_glyphs = [
            g for g in f if
            g.anchors and
            g not in combining_marks and
            g.width != 0 and
            not all([anchor.name.startswith('_') for anchor in g.anchors])
        ]

        for g in combining_marks:
            for anchor in g.anchors:
                if self.trim_tags:
                    anchor_name = trim_anchor_name(anchor.name)
                else:
                    anchor_name = anchor.name

                position = (anchor.x, anchor.y)
                am = combining_anchor_dict.setdefault(
                    anchor_name, AnchorMate(anchor))
                am.pos_name_dict.setdefault(position, []).append(g.name)

        for g in base_glyphs:
            for anchor in g.anchors:
                if self.trim_tags:
                    anchor_name = trim_anchor_name(anchor.name)
                else:
                    anchor_name = anchor.name

                position = (anchor.x, anchor.y)
                am = base_glyph_anchor_dict.setdefault(
                    anchor_name, AnchorMate(anchor))
                am.pos_name_dict.setdefault(position, []).append(g.name)

        for g in mkmk_marks:
            for anchor in g.anchors:
                if self.trim_tags:
                    anchor_name = trim_anchor_name(anchor.name)
                else:
                    anchor_name = anchor.name

                position = (anchor.x, anchor.y)
                am = mkmk_anchor_dict.setdefault(
                    anchor_name, AnchorMate(anchor))
                am.pos_name_dict.setdefault(position, []).append(g.name)

        # mark classes file
        mark_class_list = []
        for anchor_name, a_mate in sorted(combining_anchor_dict.items()):
            if anchor_name.startswith('_'):
                mc = self.make_one_mark_class(anchor_name, a_mate)
                mark_class_list.append(mc)
        mark_class_content = self.make_mark_class_content(mark_class_list)

        # mark feature file
        mark_feature_content = []
        for anchor_name, a_mate in sorted(base_glyph_anchor_dict.items()):
            mark_lookup = self.make_mark_feature_lookup(anchor_name, a_mate)
            mark_feature_content.append(mark_lookup)
            mark_feature_content.append('\n')

        # mkmk feature file
        mkmk_feature_content = []
        for anchor_name, a_mate in sorted(mkmk_anchor_dict.items()):
            if not anchor_name.startswith('_'):
                mkmk_lookup = self.make_mkmk_feature_lookup(
                    anchor_name, a_mate)
                mkmk_feature_content.append(mkmk_lookup)
                mkmk_feature_content.append('\n')

        consolidated_content = []
        if self.write_classes:
            mark_class_output = '\n'.join(mark_class_content)
            write_output(ufo_dir, self.mkclass_file, mark_class_output)
        else:
            consolidated_content.extend(mark_class_content)

        if self.write_mkmk:
            mkmk_feature_output = '\n'.join(mkmk_feature_content)
            write_output(ufo_dir, self.mkmk_file, mkmk_feature_output)
        else:
            consolidated_content.extend(mkmk_feature_content)

        consolidated_content.extend(mark_feature_content)
        consolidated_output = '\n'.join(consolidated_content)
        write_output(ufo_dir, self.mark_file, consolidated_output)

    def sort_gnames(self, glyph_list):
        '''
        Sort list of glyph names based on the glyph order
        '''
        glyph_list.sort(key=lambda x: self.glyph_order.index(x))
        return glyph_list

    def make_one_mark_class(self, anchor_name, a_mate):
        pos_gname = sorted(a_mate.pos_name_dict.items())
        mgroup_definitions = []
        mgroup_attachments = []
        single_attachments = []

        for position, g_names in pos_gname:
            pos_x, pos_y = position
            if len(g_names) > 1:
                sorted_g_names = self.sort_gnames(g_names)
                group_name = '@mGC{}_{}_{}'.format(
                    anchor_name,
                    str(pos_x).replace('-', 'n'),
                    str(pos_y).replace('-', 'n'))
                group_list = ' '.join(sorted_g_names)
                mgroup_definitions.append('{} = [ {} ];'.format(
                    group_name, group_list))
                mgroup_attachments.append(
                    'markClass {} <anchor {} {}> @MC{};'.format(
                        group_name, pos_x, pos_y, anchor_name))

            else:
                g_name = g_names[0]
                single_attachments.append(
                    'markClass {} <anchor {} {}> @MC{};'.format(
                        g_name, pos_x, pos_y, anchor_name))

        return mgroup_definitions, mgroup_attachments, single_attachments

    def make_mark_class_content(self, list_of_lists):
        '''
        The make_one_mark_class method returns a tuple of three lists per
        anchor, which may have data or not. Here those lists are assembled
        into a neatly organized text string ready for writing in a file.
        '''
        top = []
        mid = []
        bot = []
        for sublist in list_of_lists:
            group_def, group_att, single_att = sublist
            if group_def:
                top.extend(group_def)
            if group_att:
                mid.extend(group_att)
            if single_att:
                bot.extend(single_att)

        output = []
        output.extend(sorted(top))
        output.extend([''])
        output.extend(sorted(mid))
        output.extend([''])
        output.extend(sorted(bot))
        output.extend([''])
        return output

    def make_mark_feature_lookup(self, anchor_name, a_mate):

        lookup_name = 'MARK_BASE_{}'.format(anchor_name)
        open_lookup = 'lookup {} {{'.format(lookup_name)
        close_lookup = '}} {};'.format(lookup_name)

        pos_to_gname = []
        for position, g_list in a_mate.pos_name_dict.items():
            pos_to_gname.append((position, self.sort_gnames(g_list)))

        pos_to_gname.sort(key=lambda x: self.glyph_order.index(x[1][0]))
        # data looks like this:
        # [((235, 506), ['tonos']), ((269, 506), ['dieresistonos'])]

        mgroup_definitions = []
        mgroup_attachments = []
        single_attachments = []

        anchor_name_no_underscore = anchor_name.replace('_', '')

        for position, g_names in pos_to_gname:
            pos_x, pos_y = position
            if len(g_names) > 1:
                sorted_g_names = self.sort_gnames(g_names)
                group_name = '@bGC_{}_{}'.format(
                    sorted_g_names[0], anchor_name_no_underscore)
                group_list = ' '.join(sorted_g_names)
                mgroup_definitions.append('\t{} = [ {} ];'.format(
                    group_name, group_list))
                mgroup_attachments.append(
                    '\tpos base {} <anchor {} {}> mark @MC_{};'.format(
                        group_name, pos_x, pos_y, anchor_name_no_underscore))

            else:
                g_name = g_names[0]
                single_attachments.append(
                    # pos base AE <anchor 559 683> mark @MC_above;
                    '\tpos base {} <anchor {} {}> mark @MC_{};'.format(
                        g_name, pos_x, pos_y, anchor_name_no_underscore))

        output = [open_lookup]

        if mgroup_definitions:
            output.append('\n'.join(mgroup_definitions))
            output.append('\n'.join(mgroup_attachments))
        if single_attachments:
            output.append('\n'.join(single_attachments))

        output.append(close_lookup)

        return '\n'.join(output)

    def make_mkmk_feature_lookup(self, anchor_name, a_mate):
        lookup_name = 'MKMK_MARK_{}'.format(anchor_name)
        open_lookup = (
            'lookup {} {{\n'
            '\tlookupflag MarkAttachmentType @MC_{};\n'.format(
                lookup_name, anchor_name))
        close_lookup = '}} {};'.format(lookup_name)

        pos_to_gname = []
        for position, g_list in a_mate.pos_name_dict.items():
            pos_to_gname.append((position, self.sort_gnames(g_list)))

        pos_to_gname.sort(key=lambda x: self.glyph_order.index(x[1][0]))
        mkmk_attachments = []

        for position, g_names in pos_to_gname:
            pos_x, pos_y = position
            sorted_g_names = self.sort_gnames(g_names)
            for g_name in sorted_g_names:
                mkmk_attachments.append(
                    # pos mark acmb <anchor 0 763> mark @MC_above;
                    '\tpos mark {} <anchor {} {}> mark @MC_{};'.format(
                        g_name, pos_x, pos_y, anchor_name))

        output = [open_lookup]
        output.append('\n'.join(mkmk_attachments))
        output.append(close_lookup)

        return '\n'.join(output)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=(
            'Mark Feature Writer\r'
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        'input_file',
        help='input UFO file')

    parser.add_argument(
        '-t', '--trim_tags',
        action='store_true',
        default=default_trim_tags,
        help='trim casing tags from anchor names?')

    parser.add_argument(
        '-c', '--write_classes',
        action='store_true',
        default=default_write_classes,
        help='write mark classes to extra file?')

    parser.add_argument(
        '-m', '--write_mkmk',
        action='store_true',
        default=default_write_mkmk,
        help='write mark-to-mark feature file?')

    parser.add_argument(
        '-i', '--indic_format',
        action='store_true',
        default=default_indic_format,
        help='write Indic mark format?')

    parser.add_argument(
        '--mark_file',
        action='store',
        metavar='NAME',
        default=default_mark_file,
        help='name for mark feature file')

    parser.add_argument(
        '--mkmk_file',
        action='store',
        metavar='NAME',
        default=default_mkmk_file,
        help='name for mkmk feature file')

    parser.add_argument(
        '--mkclass_file',
        action='store',
        metavar='NAME',
        default=default_mkclass_file,
        help='name for mark classes file')

    parser.add_argument(
        '--abvm_file',
        action='store',
        metavar='NAME',
        default=default_abvm_file,
        help='name for above mark feature file')

    parser.add_argument(
        '--blwm_file',
        action='store',
        metavar='NAME',
        default=default_blwm_file,
        help='name for below mark feature file')

    parser.add_argument(
        '--mkgrp_name',
        action='store',
        metavar='NAME',
        default=default_mkgrp_name,
        help='name for group containing all mark glyphs')

    args = parser.parse_args()
    run(
        input_file=args.input_file,
        mark_file=args.mark_file,
        mkmk_file=args.mkmk_file,
        mkclass_file=args.mkclass_file,
        abvm_file=args.abvm_file,
        blwm_file=args.blwm_file,
        mkgrp_name=args.mkgrp_name,
        trim_tags=args.trim_tags,
        indic_format=args.indic_format,
        write_mkmk=args.write_mkmk,
        write_classes=args.write_classes)


# constants from contextual mark feature writer, to be included in future
# iterations
# kPREMarkFileName = "mark-pre.fea"
# kPOSTMarkFileName = "mark-post.fea"
# kLigaturesClassName = "LIGATURES_WITH_%d_COMPONENTS"  # The '%d' part is required
# kCasingTagsList = ['LC', 'UC', 'SC', 'AC']  # All the tags must have the same number of characters, and that number must be equal to kCasingTagSize
# kCasingTagSize = 2
# kRTLtagsList = ['_AR', '_HE']  # Arabic, Hebrew
# kIgnoreAnchorTag = "CXT"
# kLigatureComponentOrderTags = ['1ST', '2ND', '3RD', '4TH']  # Add more as necessary to a maximum of 9 (nine)

# kIndianAboveMarks = "abvm"
# kIndianBelowMarks = "blwm"
