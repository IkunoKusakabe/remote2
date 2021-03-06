#!/bin/bash

set -eu

trap catch ERR

function catch {
    echo "ERROR CATCH"
}


# 引数チェック
#if test $# -le 3; then
#  echo "ARGUMENT IS LACK."
#  echo "PLEASE INPUT MORE THAN 3 ARGUMENTS."
#  exit 1
#fi

# 差分のベースとなるブランチ
readonly DEV=develop

# SFJenkinsユーザ
readonly USER=*user*
readonly PW=*PW*

# デプロイソース置き場
readonly DEPLOY_ROOT=${JENKINS_HOME}/workspace/salesforce_deploy/

# 引数
#BRANCH_NAME=$1
#SANDBOX_NAME=$2
# 変数定義
readonly PROCESS_WS=`echo ${WORKSPACE} | sed -e 's:\\\\:\/:g'`
readonly DIFFFILE=diff.txt
readonly CODEPKG='codepkg'
readonly PYCONF=pyconf.ini
EXTRACT='false'
RENAME='false'

# パッケージ
readonly PACKAGES="ApexClass
ApexPage
ApexTrigger
ApexComponent
StaticResource
Layout
CustomObject
Workflow
"

function main {
	# developをチェックアウト
#	git checkout -b ${DEV} origin/${DEV}
	# developのマージコミットを取得
	DEV_MERGES=`git log --merges --pretty=format:"%H" origin/${DEV}`

	# 開発ブランチをチェックアウト
	git checkout -b ${BRANCH_NAME} origin/${BRANCH_NAME}

	# 開発ブランチのマージコミットを順にdevelopと照合し、最初に合致したものを保持
	for MERGE in `git log --merges --pretty=format:"%H"`
	do
		for DEV_MERGE in ${DEV_MERGES}
		do
			if test "${MERGE}" = "${DEV_MERGE}";then
				LATEST_MERGE=${MERGE}
				break 2
			fi
		done
	done

	# 開発ブランチを切った時点のdevelopと、入力されたブランチの差分を取得して書き出し
	# 0を返す「：」でファイルを初期化
	: >${DIFFFILE}
	for data in `git diff --name-status --oneline --reverse ${LATEST_MERGE}..origin/${BRANCH_NAME}`
	do
	    if test "${RENAME}" = "true";then
	        RENAME='false'
	    	EXTRACT='true'
	        continue
	    elif test "${EXTRACT}" = "true";then
			echo ${data} >>${DIFFFILE}
	    	EXTRACT='false'
	    fi
		# A = 追加/ M = 修正/ Rxxx = リネーム
	    case "${data}" in
	    	"A" | "M" )
	    		EXTRACT='true';;
	        [R]*[^.]* )
	        	RENAME='true';;
	    esac
	done

		# 差分のあったファイルをコピー
	for diff in `cat ${DIFFFILE}`
	do
		# 後方一致で/*を削除=ファイル名部分をカット
		DIRNAME=`echo ${diff%/*}`
	    # 最長マッチ(##)でメタデータ型ごとのフォルダ名を切り出し
		DIR=`echo ${DIRNAME##*/}`
	    # -以降があればカット（-meta.xmlの重複防止のため）
	    META=`echo ${diff%-*}"-meta.xml"`
	    mkdir -p ${CODEPKG}\\${DIR}
	    cp ${diff} ${CODEPKG}\\${DIR}
	    # 差分内にmeta.xmlがない場合はコピー
	    if grep ${META} ${DIFFFILE} ;then
	    	:
	    else
	    	cp ${META} ${CODEPKG}\\${DIR}
	    fi
	done

	# Pythonに渡す値を設定ファイルに出力
	{
		echo "[PROJECT]"
		echo "basedir = ."
		echo "default = ToTestDeployCheckOnly"
		echo "name = Test"
		echo "xmlnssf = antlib:com.salesforce"

		echo "[TASKDEF]"
		echo "classpath = /var/lib/jenkins/workspace/ant-salesforce.jar"
		echo "resource = com/salesforce/antlib.xml"
		echo "uri = antlib:com.salesforce"

		echo "[DEPENDS]"
		echo "name = proxy"

		echo "[TARGET]"
		echo "depends = proxy"
		echo "name = ToTestDeployCheckOnly"

		echo "[TARGETSF]"
		echo "checkonly = True"
		echo "deployroot = ${DEPLOY_ROOT}""codepkg"
		echo "maxPoll = 2000"
#		echo "maxPoll =    "
		echo "password = ${PW}"
		echo "serverurl = https://test.salesforce.com"
		echo "testLevel = RunSpecifiedTests"
		echo "username = ${USER}.${SANDBOX_NAME}"

		echo "[PACKAGE]"
		echo "members = *"
		echo "version = 29.0"
		echo "xmlns = http://soap.sforce.com/2006/04/metadata"
	} >>${PYCONF}

	# テストセクションを設定ファイルに出力
	#COUNT=0
	#echo "[TESTLIST]" >>${PYCONF}
	#for testclass in `seq 3 $#`
	#do
	#	COUNT=`expr ${COUNT} + 1`
	#    echo "test"${COUNT}" = "$3 >>${PYCONF}
	    # 引数を1つずつずらす
	#    shift
	#done

	# packageセクションを設定ファイルに出力
	COUNT=0
	echo "[PACKAGELIST]" >>${PYCONF}
	for meta in ${PACKAGES}
	do
		COUNT=`expr ${COUNT} + 1`
	    echo "package"${COUNT}" = "${meta} >>${PYCONF}
	done

	# テストセクションを設定ファイルに出力
	COUNT=0
	echo "[TESTLIST]" >>${PYCONF}
	for test in ${TESTS}
	do
		COUNT=`expr ${COUNT} + 1`
	    echo "test"${COUNT}" = "${test} >>${PYCONF}
	done
}

main