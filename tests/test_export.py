import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
SKILL=REPO/'skills'/'douyin-comments-local'
spec=importlib.util.spec_from_file_location('exporter',SKILL/'scripts'/'export.py')
exporter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class ExportBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'中文 path with spaces'
        (self.path/'raw').mkdir(parents=True)

    def batch(self,comments,number=1,video='123'):
        (self.path/'raw'/f'dom_{number:04}.json').write_text(json.dumps({
            'schema':'dyc-dom-v1','video_id':video,'comments':comments},ensure_ascii=False),encoding='utf-8')

    def run_export(self,**kw):
        return exporter.export(self.path,self.path,'123','bottom','虚构测试列表到底',**kw)

    def test_incremental_merge_sort_and_utf8(self):
        self.batch([{'cid':'a','author':'虚构甲','text':'中文😀','likes_text':'1',
                     'replies':[{'cid':'r','text':'虚构回复'}]},
                    {'cid':'b','text':'虚构高赞','likes_text':'1.2万'}])
        self.batch([{'cid':'a','text':'中文😀','likes_text':'5',
                     'replies':[{'cid':'r','text':'虚构回复','likes_text':'0'}]}],2)
        summary=self.run_export(page_count='4')
        self.assertEqual((summary['top_count'],summary['reply_count']),(2,1))
        self.assertEqual(summary['page_count_difference'],1)
        self.assertEqual(summary['completeness'],'unverified')
        tops=json.loads((self.path/'comments_top.json').read_text(encoding='utf-8'))
        self.assertEqual([c['cid'] for c in tops],['b','a'])
        self.assertEqual(tops[1]['author'],'虚构甲')
        self.assertEqual(tops[1]['likes_approx'],5)
        self.assertIn('中文😀',(self.path/'评论全文.md').read_text(encoding='utf-8'))

    def test_missing_likes_stays_unknown_and_markup_is_escaped(self):
        text='<img src=x> [link](https://invalid.example) `x` $(not-a-command)'
        self.batch([{'cid':'a','text':text}])
        self.run_export()
        item=json.loads((self.path/'comments_top.json').read_text(encoding='utf-8'))[0]
        self.assertIsNone(item['likes_approx'])
        self.assertEqual(item['text'],text)
        md=(self.path/'评论全文.md').read_text(encoding='utf-8')
        self.assertIn('&lt;img',md)
        self.assertIn(r'\[link\]',md)

    def test_fingerprints_respect_parents(self):
        reply={'author':'虚构乙','text':'一样的虚构回复','time_text':'昨天'}
        self.batch([{'cid':'a','text':'父楼甲','replies':[reply]},
                    {'cid':'b','text':'父楼乙','replies':[reply]}])
        summary=self.run_export()
        self.assertEqual(summary['reply_count'],2)
        self.assertEqual(summary['synthetic_id_count'],2)

    def test_distinct_ids_with_identical_text_are_retained(self):
        self.batch([{'cid':'a','text':'同一虚构内容'},{'cid':'b','text':'同一虚构内容'}])
        self.assertEqual(self.run_export()['top_count'],2)

    def test_empty_input_is_failure_without_report(self):
        self.batch([])
        with self.assertRaises(ValueError):self.run_export()
        self.assertFalse((self.path/'comments_top.json').exists())

    def test_mixed_video_is_failure_before_output(self):
        self.batch([{'cid':'a','text':'虚构评论'}])
        self.batch([{'cid':'b','text':'另一视频'}],2,'456')
        with self.assertRaises(ValueError):self.run_export()
        self.assertFalse((self.path/'capture_summary.json').exists())

    def test_conflicting_reply_parent_is_rejected(self):
        self.batch([{'cid':'a','text':'父楼一','replies':[{'cid':'r','text':'回复'}]},
                    {'cid':'b','text':'父楼二','replies':[{'cid':'r','text':'回复'}]}])
        with self.assertRaises(ValueError):self.run_export()

    def test_bad_reply_shape_is_rejected(self):
        self.batch([{'cid':'a','text':'正文','replies':'not-an-array'}])
        with self.assertRaises(ValueError):self.run_export()

    def test_report_overwrite_requires_opt_in(self):
        self.batch([{'cid':'a','text':'正文'}])
        self.run_export()
        with self.assertRaises(ValueError):self.run_export()
        self.run_export(overwrite=True)

    def test_cli_empty_input_is_nonzero(self):
        self.batch([])
        proc=subprocess.run([sys.executable,str(SKILL/'scripts'/'export.py'),str(self.path),
            '--video-id','123','--scope','tool-error','--stop-reason','虚构工具失败'],capture_output=True)
        self.assertEqual(proc.returncode,3)


class InstallationBehavior(unittest.TestCase):
    def test_install_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination=Path(tmp)/'中文 install space'
            command=[sys.executable,str(REPO/'install.py'),'--destination',str(destination)]
            first=subprocess.run(command,capture_output=True)
            self.assertEqual(first.returncode,0,first.stderr)
            target=destination/'douyin-comments-local'
            self.assertTrue((target/'SKILL.md').is_file())
            self.assertTrue((target/'LICENSE').is_file())
            marker=target/'marker.txt'
            marker.write_text('user file',encoding='utf-8')
            second=subprocess.run(command,capture_output=True)
            self.assertEqual(second.returncode,2)
            self.assertEqual(marker.read_text(encoding='utf-8'),'user file')
            doctor=subprocess.run([sys.executable,str(target/'scripts'/'doctor.py')],capture_output=True)
            self.assertEqual(doctor.returncode,0,doctor.stderr)
            result=json.loads(doctor.stdout)
            self.assertEqual(result['browser_connection'],'not_checked')

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination=Path(tmp)/'not-created'
            proc=subprocess.run([sys.executable,str(REPO/'install.py'),'--destination',str(destination),'--dry-run'],capture_output=True)
            self.assertEqual(proc.returncode,0)
            self.assertFalse(destination.exists())

    @unittest.skipUnless(shutil.which('node'),'Node.js optional; needed only for DOM reader unit tests')
    def test_reader_unit_cases(self):
        proc=subprocess.run(['node',str(REPO/'tests'/'test_reader.cjs')],capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr.decode('utf-8',errors='replace'))


if __name__=='__main__':unittest.main()
