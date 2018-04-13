# coding: UTF-8

# xmlを読み書きするためのモジュール
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
# 環境変数取得のためのモジュール
import os
# iniファイルを扱うためのモジュール(py2ver)
import ConfigParser

class XmlCreator:
	# iniファイル読み込み(py2ver)
	conf = ConfigParser.SafeConfigParser()
	conf.read('../salesforce_deploy/pyconf.ini')
	# 出力先
	BUILD_XML = 'buildToTest.xml'
	PACKAGE_XML = 'package.xml'

	## 実行
	def execute(self):
		
		self.__createBuildXml()
		self.__createPackageXml()
		self.outputXml(self.project,self.BUILD_XML)
		self.outputXml(self.package,self.PACKAGE_XML)
	
	## build.xmlの作成
	def __createBuildXml(self):

		# projectノード作成
		self.project = ET.Element('project')
		self.project.set('basedir', self.conf.get('PROJECT','basedir'))
		self.project.set('default', self.conf.get('TARGET','name'))
		self.project.set('name', self.conf.get('PROJECT','name'))
		self.project.set('xmlns:sf', self.conf.get('PROJECT','xmlnssf'))

		# taskdefノード作成
		taskdef = ET.SubElement(self.project,'taskdef',
								{'resource':self.conf.get('TASKDEF','resource'),
								'classpath':self.conf.get('TASKDEF','classpath'),
								'uri':self.conf.get('TASKDEF','uri')})

		# targetノード作成(プロキシ設定)
#		target1 = ET.SubElement(self.project,'target')
#		target1.set('name',self.conf.get('DEPENDS','name'))

		# setproxyノード作成
#		setproxy = ET.SubElement(target1,'setproxy',
#								{'proxyhost':self.conf.get('DEPENDSSETPROXY','proxyhost'),
#								'proxyport':self.conf.get('DEPENDSSETPROXY','proxyport'),
#								'proxyuser':self.conf.get('DEPENDSSETPROXY','proxyuser'),
#								'proxypassword':self.conf.get('DEPENDSSETPROXY','proxypassword')})

		# targetノード作成(デプロイ)
		target2 = ET.SubElement(self.project,'target',
								{'name':self.conf.get('TARGET','name')})
#								{'name':self.conf.get('TARGET','name'),
#								'depends':self.conf.get('TARGET','depends')})

		# sf:deployノード作成
		deploy = ET.SubElement(target2,'sf:deploy',
								{'username':self.conf.get('TARGETSF','username'),
								'password':self.conf.get('TARGETSF','password'),
								'serverurl':self.conf.get('TARGETSF','serverurl'),
								'deployRoot':self.conf.get('TARGETSF','deployRoot'),
								'maxPoll':self.conf.get('TARGETSF','maxPoll'),
								'testLevel':self.conf.get('TARGETSF','testLevel'),
								'checkOnly':self.conf.get('TARGETSF','checkOnly')})

		# テストクラスをファイルを読み込んで書き出す
	#	with open(self.conf.get('TESTLIST','tests'), 'r') as f:
	#		for row in f:
	#			test = ET.SubElement(deploy, 'runTest')
				# strip=両端からスペース・タブ・改行を除去
	#			test.text = row.strip()
		# セクションのkey = valのセットを辞書で取得しループ
		for row in dict(self.conf.items("TESTLIST")).values():
			test = ET.SubElement(deploy, 'runTest')
			# strip=両端からスペース・タブ・改行を除去
			test.text = row.strip()

	## package.xmlの作成
	def __createPackageXml(self):

		# Packageノード作成
		self.package = ET.Element('Package')
		self.package.set('xmlns',self.conf.get('PACKAGE','xmlns'))

		# メタデータをファイルを読み込んで書き出す
	#	with open(self.conf.get('PACKAGELIST','packs'), 'r') as pack:
	#		for data in pack:
				# typesノードを作成
	#			types = ET.SubElement(self.package,'types')
				# membersノードを作成
	#			members = ET.SubElement(types,'members')
	#			members.text = self.conf.get('PACKAGE','members')
				# nameノードを作成
	#			name = ET.SubElement(types,'name')
	#			name.text = data.strip()
			# セクションのkey = valのセットを辞書で取得しループ
		for meta in dict(self.conf.items("PACKAGELIST")).values():
			types = ET.SubElement(self.package,'types')
			members = ET.SubElement(types,'members')
			members.text = self.conf.get('PACKAGE','members')
			name = ET.SubElement(types,'name')
			name.text = meta.strip()

		# versionノードを作成
		version = ET.SubElement(self.package,'version')
		version.text = self.conf.get('PACKAGE','version')
	
	## 渡されたxmlを解析し、インデントを追加して出力する
	def outputXml(self,xml_name,file):
		string = unicode(ET.tostring(xml_name), 'utf-8')
		pretty_string = minidom.parseString(string).toprettyxml(indent='  ')
		with open(file, 'w') as xml:
			xml.write(pretty_string)


creator = XmlCreator()
creator.execute()
