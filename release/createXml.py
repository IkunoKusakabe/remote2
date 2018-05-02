# coding: UTF-8

# xmlを読み書きするためのモジュール
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
# 環境変数取得のためのモジュール
import os
# iniファイルを扱うためのモジュール(py2ver)
import ConfigParser

class Xml_Creator:
	# 出力先
	BUILD_XML = 'build.xml'
	PACKAGE_XML = 'package.xml'

	def __init__(self):
		# iniファイル読み込み(py2ver)
		self._conf = ConfigParser.SafeConfigParser()
		self._conf.read('../salesforce_deploy/pyconf.ini')
		# 不正な値がある場合True
		self._empty_value_flag = False

	## 実行
	def execute(self):
		self._check_blank_value()
		self._create_build_xml()
		self._create_package_xml()
		self._output_xml(self.project,self.BUILD_XML)
		self._output_xml(self.package,self.PACKAGE_XML)
	
	## 設定値に空白がある場合は例外を投げる
	def _check_blank_value(self):

		for section in self._conf.sections():
			print('SECTION : ' + section)
			for key in dict(self._conf.items(section)).keys():
				value = self._conf.get(section, key).strip()
				if not(value):
					print(key + '\'s value is EMPTY!')
					self._empty_value_flag = True

		if self._empty_value_flag:
			raise ValueError('EMPTY VALUE IN PROPERTY FILE')

	## build.xmlの作成
	def _create_build_xml(self):

		# projectノード作成
		self.project = ET.Element('project')
		self.project.set('basedir', self._conf.get('PROJECT','basedir').strip())
		self.project.set('default', self._conf.get('TARGET','name').strip())
		self.project.set('name', self._conf.get('PROJECT','name').strip())
		self.project.set('xmlns:sf', self._conf.get('PROJECT','xmlnssf').strip())

		# taskdefノード作成
		taskdef = ET.SubElement(self.project,'taskdef',
								{'resource':self._conf.get('TASKDEF','resource').strip(),
								'classpath':self._conf.get('TASKDEF','classpath').strip(),
								'uri':self._conf.get('TASKDEF','uri').strip()})

		# targetノード作成(プロキシ設定)
#		target1 = ET.SubElement(self.project,'target')
#		target1.set('name',self._conf.get('DEPENDS','name').strip())

		# setproxyノード作成
#		setproxy = ET.SubElement(target1,'setproxy',
#								{'proxyhost':self._conf.get('DEPENDSSETPROXY','proxyhost').strip(),
#								'proxyport':self._conf.get('DEPENDSSETPROXY','proxyport').strip(),
#								'proxyuser':self._conf.get('DEPENDSSETPROXY','proxyuser').strip(),
#								'proxypassword':self._conf.get('DEPENDSSETPROXY','proxypassword').strip()})

		# targetノード作成(デプロイ)
		target2 = ET.SubElement(self.project,'target',
								{'name':self._conf.get('TARGET','name').strip()})
#								{'name':self._conf.get('TARGET','name').strip(),
#								'depends':self._conf.get('TARGET','depends').strip()})

		# sf:deployノード作成
		deploy = ET.SubElement(target2,'sf:deploy',
								{'username':self._conf.get('TARGETSF','username').strip(),
								'password':self._conf.get('TARGETSF','password').strip(),
								'serverurl':self._conf.get('TARGETSF','serverurl').strip(),
								'deployRoot':self._conf.get('TARGETSF','deployRoot').strip(),
								'maxPoll':self._conf.get('TARGETSF','maxPoll').strip(),
								'testLevel':self._conf.get('TARGETSF','testLevel').strip(),
								'checkOnly':self._conf.get('TARGETSF','checkOnly').strip()})

		# テストクラスをファイルを読み込んで書き出す
	#	with open(self._conf.get('TESTLIST','tests'), 'r') as f:
	#		for row in f:
	#			test = ET.SubElement(deploy, 'runTest')
				# strip=両端からスペース・タブ・改行を除去
	#			test.text = row.strip()
		# セクションのkey = valのセットを辞書で取得しループ
		for row in dict(self._conf.items("TESTLIST")).values():
			test = ET.SubElement(deploy, 'runTest')
			# strip=両端からスペース・タブ・改行を除去
			test.text = row.strip()

	## package.xmlの作成
	def _create_package_xml(self):

		# Packageノード作成
		self.package = ET.Element('Package')
		self.package.set('xmlns',self._conf.get('PACKAGE','xmlns').strip())

		# メタデータをファイルを読み込んで書き出す
	#	with open(self._conf.get('PACKAGELIST','packs'), 'r') as pack:
	#		for data in pack:
				# typesノードを作成
	#			types = ET.SubElement(self.package,'types')
				# membersノードを作成
	#			members = ET.SubElement(types,'members')
	#			members.text = self._conf.get('PACKAGE','members')
				# nameノードを作成
	#			name = ET.SubElement(types,'name')
	#			name.text = data.strip()
			# セクションのkey = valのセットを辞書で取得しループ
		for meta in dict(self._conf.items("PACKAGELIST")).values():
			types = ET.SubElement(self.package,'types')
			members = ET.SubElement(types,'members')
			members.text = self._conf.get('PACKAGE','members')
			name = ET.SubElement(types,'name')
			name.text = meta.strip()

		# versionノードを作成
		version = ET.SubElement(self.package,'version')
		version.text = self._conf.get('PACKAGE','version').strip()
	
	## 渡されたxmlを解析し、インデントを追加して出力する
	def _output_xml(self,xml_name,file):
		string = unicode(ET.tostring(xml_name), 'utf-8')
		pretty_string = minidom.parseString(string).toprettyxml(indent='  ')
		with open(file, 'w') as xml:
			xml.write(pretty_string)


creator = Xml_Creator()
creator.execute()
