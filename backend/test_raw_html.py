import re

html_snippet = """
</script>
</head>

<body onload="DocLoaded()">
    <div id="div-all-modals-placeholder">
                <!-- The modal screen -->
        <div id="generic-modal" class="modal-screen">
            <!-- Modal content -->
                    <div class="modal-content"
             style="overflow: hidden;"
             role="alertdialog"
             aria-modal="true"
             aria-labelledby="generic-modal"
             >
                    			<div id="generic-modal-header" class="modal-header">
            	<div id="generic-modal-title" class="modal-title">
				            placeholder-title		        </div>
		        	</div>
                <div style="max-height: 70vh;overflow:auto">
            <div id="generic-modal-content"
                 class="alertMessage"
                 style="text-align: left;">
                            </div>
        </div>
                <div class="buttonsBox" style="text-align: right;">
            <div class="button-box-left"></div>
            
                            <!-- closes the modal -->
                <button id="generic-modal-button-close"
                        class="close">
                    Cerrar                </button>
            
            
            
                    </div>
                </div>
                </div>
                        <!-- The modal screen -->
        <div id="generic-confirm-modal" class="modal-screen">
            <!-- Modal content -->
                    <div class="modal-content"
             style="overflow: hidden;"
             role="alertdialog"
             aria-modal="true"
             aria-labelledby="generic-confirm-modal"
             >
                    			<div id="generic-confirm-modal-header" class="modal-header">
            	<div id="generic-confirm-modal-title" class="modal-title">
				            placeholder-title		        </div>
		        	</div>
                <div style="max-height: 70vh;overflow:auto">
            <div id="generic-confirm-modal-content"
                 class="alertMessage"
                 style="text-align: left;">
                            </div>
        </div>
                <div class="buttonsBox" style="text-align: right;">
            <div class="button-box-left"></div>
            
            
            
                            <button id="generic-confirm-modal-action-confirm-cancel"
                        class=""
                        onclick="">
                    Cancelar                </button>
                            <button id="generic-confirm-modal-action-confirm-ok"
                        class="blue-button"
                        onclick="">
                    Bien                </button>
            
                    </div>
                </div>
                </div>
                        <!-- The modal screen -->
        <div id="generic-activity-modal" class="modal-screen">
            <!-- Modal content -->
                    <div class="modal-content"
             style="overflow: hidden;"
             role="alertdialog"
             aria-modal="true"
             aria-labelledby="generic-activity-modal"
             >
                    			<div id="generic-activity-modal-header" class="modal-header">
            	<div id="generic-activity-modal-title" class="modal-title">
				            placeholder-title		        </div>
		        	</div>
                <div style="max-height: 70vh;overflow:auto">
            <div id="generic-activity-modal-content"
                 class="alertMessage"
                 style="text-align: center;">
                            <div id="" class="stacked-glyph show-glyph  " style="width: fit-content"                  tabindex="-1" style="">
                                    <i id="" class="xrx-spinner_alt bottom-glyph xrxsize-128 theme-75"></i>
                    <i id="" class="xrx-spinner xrxsize-128 theme-700" style="visibility: "></i>
                            </div>
                <div id="generic-activity-modal-body-text"></div>
                </div>
        </div>
                <div class="buttonsBox" style="text-align: right;">
            <div class="button-box-left"></div>
            
            
            
                            <button id="generic-activity-modal-action-cancel"
                        class="blue-button"
                        onclick="">
                    Cancelar                </button>
            
                    </div>
                </div>
                </div>
            </div>
                <header id="globalHeader" class="global-header">
                <div>
                    <a href="#main-content" class="skip">Ir al contenido principal</a>
                </div>
                <div class="header-productinfo" style=";">
                    <div>
                        <div id="xeroxLogo">
                            <a class="off-box-link" href="http://www.xerox.com" title="xerox.com">
                                <img src="data:image/svg+xml;base64,PHN2ZyBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWlkWU1pZCBtZWV0IiB2aWV3Qm94PSIwIDAgODUzLjI2ODcgMTczLjYzOTMiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0ibTgxNS41ODg2IDYuMzk0M2gtNS44MXYtMy41aDE1LjM3MTR2My41aC01LjgxMDh2MTguOTkzOGgtMy43NXptMTMuMTg1OS0zLjVoNi40MzY1bDUuNjIyMiAxOC45OTg3aC4zNzY4bDUuNjIyMi0xOC45OTg3aDYuNDM2NXYyMi40OTM4aC0zLjYyMjZ2LTE4Ljk5MzhoLS4zNzY4bC01LjY4NTcgMTguOTkzOGgtNS4xMjM2bC01LjY4NjItMTguOTkzOGgtLjM3NjR2MTguOTkzOGgtMy42MjI5eiIgZmlsbD0iIzIzMWYyMCIvPjxnIGZpbGw9IiNkOTIyMzEiPjxwYXRoIGQ9Im01ODQuNTI2MSA4Ni43NWMwLTI5LjE2OTItMTEuMjIzMy01NC45OTIyLTQxLjA5NjEtNTQuOTkyMi0yOS45MyAwLTQxLjQ2MTMgMjUuODIzLTQxLjQ2MTMgNTQuOTkyMnMxMS41MzEzIDU1LjAyIDQxLjQ2MTMgNTUuMDJjMjkuODcyOCAwIDQxLjA5NjEtMjUuODUgNDEuMDk2MS01NS4wMm00NC4wNDk1IDBjMCA0OS44NzI0LTM1LjI3MjYgODYuNzQ4NS04NS4yMyA4Ni43NDg1LTUwLjg1NjQgMC04NS40MjY2LTM1LjMyOTEtODUuNDI2Ni04Ni43MjA4LS4wMDAzLTQ4LjYwNjkgMzQuMTE5My04Ni43Nzc3IDg1LjQyNjMtODYuNzc3NyA0OS45NTc3IDAgODUuMjMgMzYuOTA1IDg1LjIzIDg2Ljc1Ii8+PHBhdGggZD0ibTI4OC41MTM2IDcwLjY2aC03Ny4yNTY3YTUyLjg3NTkgNTIuODc1OSAwIDAgMSA0Ljg4MDgtMTUuOTc3MmM2LjkzMy0xMy44OTU2IDIwLjAxMzQtMjIuNzU2NSAzNi4zNTY0LTIyLjc1NjUgMjIuMzc2MiAwIDM2LjAxOTUgMTUuMTkgMzYuMDE5NSAzNy43MjE0em00MC4wOTYzLjY3NDFjLTIuMDUyMy0yMi41MzA2LTEwLjMyMzMtNDAuNzAxMy0yNC4yMTg4LTUyLjk2NjQtMTMuMzA0My0xMS44NDI2LTMxLjE2NjktMTguMjgzLTUzLjMxNzItMTguMjgzLTE2LjMyODcgMC0zNi45NjA5IDUuNjU0Ni01Mi4xNTA1IDE4LjExNDgtMTguMDczNCAxNC45MDkxLTMyLjEzODQgMzguMTk4NS0zMi4xMzg0IDY5LjU5MDUgMCAyNy4wNiA4LjgxODMgNDguODMyNCAyNC42MTMgNjMuNTQyNiAxNS40NDMxIDE0LjQ1ODUgMzcuMzY4NyAyMi4zMDcxIDY0LjQ3MTkgMjIuMzA3MSAyMS44NTQ4IDAgNDguMjY4My04LjIxMzMgNTkuNTItMTUuMjE4NSAzLjk5MzUtMi40MTgxIDUuMjU5Mi0zLjUxNTIgNC4yNjEzLTcuNTFsLTcuMTAzMS0yMC4wMjcxYy0uNzg3Ni0zLjIwNTgtNC40NzE1LTQuMDc4OC03LjM5OC0yLjU4ODJhMTQ0LjA2MDcgMTQ0LjA2MDcgMCAwIDEgLTEzLjcyNjcgNi4xODg3Yy05Ljc2IDMuNjI5My0xOS45NTY5IDYuMTAzMy0yOS41NjI4IDYuMTAzMy0yMC4yNjYzIDAtMzEuODctNS41MTM0LTQwLjY3MzctMTUuNzUxMy01LjU5ODItNi40NjkzLTguODc0OC0xNC41OTkxLTkuODg4NC0yNC4wNWgxMTEuOTY4YzQuMDIxMSAwIDUuODUtMi43ODUzIDUuODUtNy41OTU4di04LjA0NTNjMC0zLjk2NjMtLjE2ODItMTAuMDctLjUwNjYtMTMuODExNCIvPjxwYXRoIGQ9Im0zNjguODYzMSAyMy45OTM1YzEyLjY1NzktMTYuMzE0MyAzMi40MzE2LTIzLjc2ODggNjQuNzc5Ni0yMy43Njg4YTExNS41OSAxMTUuNTkgMCAwIDEgMjIuNzg0MSAyLjI3OTNjMy43OTc2LjkwMDYgNC40MTcgMy45MDg3IDMuNjg1MiA3LjgxOTJsLTMuODI1MiAxOC44NDYxYy0uODQzNCAzLjUxNjktMS44NTY0IDQuNTI5My00LjYxMjggNC41MjkzYTE3LjQyIDE3LjQyIDAgMCAxIC0yLjI3ODItLjE2OTVjLTIuNjcyOC0uMzY0Ni0xMC4yOTU4LTEuMTgxMS0xMy40NDU4LTEuMTgxMS0xNi4wOSAwLTIzLjcxMyA0LjAyMjMtMjkuNDY0OCAxMC4wNDI3LTYuNjgxNCA3LjE3MjItNi44Nzg1IDE3LjcyMTQtNi44Nzg1IDM2LjU5NXY4My43OTYyYzAgNS41MTI4LTIuNDE4MSA4LjYwNjktOC4zMjU2IDguNjA2OWgtMjUuNTk2OGMtNS40NTY5IDAtNy44Mi0yLjcwMDYtOC4yNzA5LTguNjA2OXYtODIuMjc2OGMwLTI5Ljk1NzUgMS43MzE0LTQzLjk5MzcgMTEuNDUtNTYuNTExNiIvPjxwYXRoIGQ9Im03MTUuODMxMSA1OC44NzMyYzUuNzIzOC01Ljk5MSAxOS4wNzE0LTIyLjQ3NDEgMzMuODUzNy01MC4zNzc1IDIuNTE3Mi00Ljc4MjkgNC43ODExLTUuOTkxNyA4LjA4NjUtNS45OTE3aDI3LjQ1MjljMi41MDQ2IDAgNS40NTcgMS4yMDg4IDMuODU0IDUuOTkxNy0xMC45MTM5IDMyLjM3NS0zNS44MzYyIDYwLjgxMzItNDkuNjE4OCA3NS40OTc1IDE1LjAwNjUgMTQuMjMyIDQxLjY4NiA0Ny45MzEyIDU0LjIxNzIgODEuMDExIDEuMTEyMSAyLjk4MTEuNTYyOSA2LjM4NDYtNS42OTYgNi4zODQ2aC0zMi44NTMzYy0zLjM3NTggMC02LjA5MDgtLjMxLTguMzU0NS01Ljk2MjgtOC4xNDMxLTIwLjI4MTktMjAuODcxMy00MS42MDI1LTM1LjQxNDUtNTUuNjExNi0xNS45MjE0IDE2Ljg3NzgtMjcuOTg3NSAzNy42MzY3LTM2LjExNzQgNTUuNjExNi0yLjAyNDYgNC40MTU3LTMuOTkzNCA1Ljk2MjgtOC4zNCA1Ljk2MjhoLTMwLjE0Yy0yLjA0IDAtNC4wOTE4LTIuMzM0Ny0yLjc1Ny01Ljk2MjggOC45Ni0yNC41ODUzIDI2LjgwODItNTUuMTg5MyA1Mi40MDQ2LTc4LjIyNy0yMC4xMzk1LTI0LjI0Ny0zOS40MjIyLTUzLjgxLTQ3LjAxOC03OC43MDMzLTEuMTY2Ny0zLjc0MTcuODMwOS01Ljk5MTcgMy42NDM4LTUuOTkxN2gzNS4zNzEyYzMuODY4NCAwIDUuODY1NCAxLjU3NDcgNy43NSA1Ljk5MTcgOC43MiAyMC4yODA2IDIwLjYwNTEgMzkuNjA0OSAyOS42NzYzIDUwLjM3NzUiLz48cGF0aCBkPSJtODIuMjMgNTguODczMmM1LjcxLTUuOTkxIDE5LjA0MzYtMjIuNDc0MSAzMy44ODE3LTUwLjM3NzUgMi40ODkxLTQuNzgyOSA0LjcxMTQtNS45OTE3IDguMDU4NC01Ljk5MTdoMjcuNTEwNmMyLjQ0NjkgMCA1LjQgMS4yMDg4IDMuNzk3NCA1Ljk5MTctMTAuOTcxNSAzMi4zNzUtMzUuODY1IDYwLjgxMzItNDkuNjQ3NiA3NS40OTc1IDE1LjA0ODUgMTQuMjYwOSA0MS43MTQ5IDQ3Ljk1ODMgNTQuMzE2OSA4MS4wMTEgMS4wNjg4IDIuOTgxMS41MDUzIDYuMzg0Ni01LjgwODMgNi4zODQ2aC0zMi44ODI3Yy0zLjM5IDAtNS45NjM0LS4zMS04LjI4MzYtNS45NjI4LTguMTMtMjAuMjgxOS0yMC45LTQxLjYwMjUtMzUuNDE0NC01NS41ODI4LTE1LjkwNjkgMTYuODQ5LTI3Ljk4ODQgMzcuNjM2OC0zNi4xNjA3IDU1LjU4MjgtMS45NTQzIDQuNDE1Ny0zLjkyMzEgNS45NjI4LTguMjgzNSA1Ljk2MjhoLTMwLjEyNjRjLTIuMDI0NyAwLTQuMDc4MS0yLjMzNDctMi43ODM0LTUuOTYyOCA4Ljk3MjEtMjQuNTg1MyAyNi44MzQ2LTU1LjE4OTMgNTIuMzQ2My03OC4yMjctMTkuOTcwNy0yNC4yNDctMzkuMzUxNC01My44MDk4LTQ2Ljk0NTktNzguNzAzMy0xLjE1MzUtMy43NDE3Ljg3MTEtNS45OTE3IDMuNjQyNi01Ljk5MTdoMzUuMzcyNmMzLjg1MjIgMCA1LjgyMjggMS41NzQ3IDcuNzc3MSA1Ljk5MTcgOC42NSAyMC4yODA2IDIwLjU3NTcgMzkuNjA0OSAyOS42MzMyIDUwLjM3NzUiLz48L2c+PC9zdmc+" height="20" alt="Xerox">
                            </a>
                        </div>
                        <div id="productName"><sup> </sup>VersaLink<sup>&reg; </sup>B415 Multifunction Printer </div>
                    </div>
                </div>
                <div id="navBar" $alignArabicText><nav id="navBarItems" aria-label="site" $alignArabicText>			<div class="navBarItem selected ">
				<a href="/stat/welcome.php" id="tab_stat">
					<div class="navName" >Principal</div>
				</a>
			</div>
			<div class="navBarItem selectable ">
				<a href="/jobs/active.php" id="tab_jobs">
					<div class="navName" >Trabajos</div>
				</a>
			</div>
			<div class="navBarItem selectable ">
				<a href="/print/print.php" id="tab_print">
					<div class="navName" >Impresión</div>
				</a>
			</div>
			<div class="navBarItem selectable ">
				<a href="/scan/new_info.php?show=temp" id="tab_scan">
					<div class="navName" >Exploración</div>
				</a>
			</div>
			<div class="navBarItem selectable ">
				<a href="/addressbook/viewContact.php" id="tab_addressbook">
					<div class="navName" >Libreta de direcciones</div>
				</a>
			</div>
			<div class="navBarItem selectable ">
				<a href="/properties/blank.php" id="tab_properties">
					<div class="navName" >Propiedades </div>
				</a>
			</div>
			<div class="navBarItem selectable last">
				<a href="/support/support.php" id="tab_support">
					<div class="navName" >Asistencia</div>
				</a>
			</div>
			</nav>

			<div class="navBarItem last" id="loginButton">
				<span id="globalHeaderLoginBtn" tabindex="0" class="loginSpan" onclick="Javascript:OpenLogin('stat')">Inicio de sesión</span>
			</div></div>
            </header>
                        <div id="timeout-alert">
                <div id="timeout-alert-msg-div">
                    El tiempo de espera del dispositivo se va a agotar debido a la inactividad.                    <br>
                    Será desconectado si no se detecta ningún tipo de acción.                    <br>
                    Seleccione Aceptar para continuar trabajando.                </div>
                <div id="timeout-alert-btn-div">
                    <button id="timeout-alert-ok">Bien</button>
                </div>
            </div>
                        <main id="main-content" class="mainContentNoSideBar" tabindex="-1">
            

<h1 class="withIcon">Contadores de uso</h1>

<!-- #bbmark refresh button -->
<div class="horizButtonBarAboveTableLeft">
    <button id="refreshBtn">Actualizar </button>
    <button id="downloadBtn" >
        Descargar archivo en el PC    </button>
</div>

<div class="boundingBox normalSpacing noTop noBottom">
    <div class="boxBody tableBody">
        <table cellspacing="0" cellpadding="0" class="tableDiv">
            <thead>
                <tr class="header">
                    <th class="first">Contador</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
            <tr class="odd"><td width="50%">Total de impresiones</td><td style="text-align: center;">798</td></tr>
<tr class="even"><td width="50%">&nbsp;&nbsp;&nbsp;Impresiones en negro</td><td style="text-align: center;">798</td></tr>
<tr class="odd"><td width="50%">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Impresiones copiadas en negro</td><td style="text-align: center;">87</td></tr>
<tr class="even"><td width="50%">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Impresiones impresas en negro</td><td style="text-align: center;">711</td></tr>
<tr class="odd"><td width="50%">&nbsp;&nbsp;&nbsp;Impresiones individuales</td><td style="text-align: center;">798</td></tr>
<tr class="even"><td width="50%">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Impresiones individuales en negro</td><td style="text-align: center;">798</td></tr>
<tr class="odd"><td width="50%">&nbsp;&nbsp;&nbsp;Impresiones iguales en A4</td><td style="text-align: center;">798</td></tr>
<tr class="even"><td width="50%">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Impresiones iguales negro en A4</td><td style="text-align: center;">798</td></tr>
<tr class="odd"><td width="50%">&nbsp;&nbsp;&nbsp;Impresiones de fax interno</td><td style="text-align: center;">0</td></tr>
<tr class="even"><td width="50%">&nbsp;&nbsp;&nbsp;Impresiones impresas de imágenes guardadas</td><td style="text-align: center;">0</td></tr>
<tr class="odd"><td width="50%">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Impresiones impresas de imágenes en negro guardadas</td><td style="text-align: center;">0</td></tr>
<tr class="even"><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr class="odd"><td width="50%">Hojas copiadas en negro</td><td style="text-align: center;">61</td></tr>
<tr class="even"><td width="50%">Hojas impresas en negro</td><td style="text-align: center;">527</td></tr>
<tr class="odd"><td width="50%">Hojas del fax interno</td><td style="text-align: center;">0</td></tr>
<tr class="even"><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr class="odd"><td width="50%">Hojas a dos caras copiadas en blanco y negro</td><td style="text-align: center;">26</td></tr>
<tr class="even"><td width="50%">Hojas a dos caras impresas en blanco y negro</td><td style="text-align: center;">184</td></tr>
<tr class="odd"><td width="50%">Hojas a 2 caras del fax interno</td><td style="text-align: center;">0</td></tr>
<tr class="even"><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr class="odd"><td width="50%">Imágenes enviadas en fax interno</td><td style="text-align: center;">0</td></tr>
<tr class="even"><td width="50%">Imágenes de e-mail enviadas</td><td style="text-align: center;">0</td></tr>
<tr class="odd"><td width="50%">Imágenes de fax de servidor enviadas</td><td style="text-align: center;">0</td></tr>
<tr class="even"><td width="50%">Imágenes de escaneado en red enviadas</td><td style="text-align: center;">0</td></tr>
<tr class="odd"><td width="50%">Impresiones desde encendido</td><td style="text-align: center;">572</td></tr>
            </tbody>
        </table>
    </div>
    <div class="clearFloats"></div>
</div>
<div class="horizButtonBarBelowTableRight">
    <button type="button" id="closeButton">Cerrar</button>
</div>

<script> var helpPath = "/help/es";</script>    <script>
        function OpenHelpWindow() {
            var context;
            var anchor = '';
            var helpContext;

            if (HELP_CONTEXT) {
                context = HELP_CONTEXT;
                var contextParts = context.split('#');
                context = contextParts[0];
                anchor = contextParts[1] ? '#' + contextParts[1] : '';
            }
            
            if ("" != context) {
                helpContext = "/" + context + ".html";
            }
             
            window.open(helpPath + helpContext + anchor, "helpWindow");
        }
    </script>
    
	<footer id="globalFooter">
		<div id="global-help-btn" tabindex="0" onclick="javascript:OpenHelpWindow()"><i class="xrx-help" style="font-size: 36px"></i><br>Ayuda</div>&copy;2017-2024&nbsp;Xerox Corporation. Reservados todos los derechos.<br>Xerox&reg; y&nbsp;VersaLink&reg;&nbsp;son marcas comerciales de<br>Xerox Corporation en los Estados Unidos y/o en otros países.
		<br />
		<div class="toolbar">
			<a href="/links.php" target="_top">Índice</a>
			 | <a href="/sitemap.php" target="_top">Mapa del sitio</a>
			 | <a href="/legal.php" target="_top">Extra Oficio</a></div>
	</footer>
<form action="/dummypost/xerox.set" method="post">
<div>
    <input type="hidden" name="webServices.supportDLMs[edgeCli].immediateDataCollection" value="TRUE">
    <input type="hidden" name="_fun_function" value="HTTP_Set_Config_Non_Sec_fn">
    <input type="hidden" name="NextPage" value="/activityIndicator.php?activity=UsageCounterDownloadActivity">
    <input type="hidden" name="CSRFToken" value="ac7a852821846034e10cffd57e7bf0e5c1f75a6c82ec4dd83e8e1b17a53b92c6d73a367520d1797a3be253eb3d9f9ac5fa6f8f4e9d039d2c2b6f5334e44af309">
</div>
</form>

            </main>
            </div>
            </body>
</html>
"""

two_sided_copied = re.search(r'Hojas a dos caras copiadas en blanco y negro.*?<td[^>]*>\s*([\d,.]+)\s*<', html_snippet, re.I | re.DOTALL)
if two_sided_copied:
    print("Copied:", two_sided_copied.group(1))

two_sided_printed = re.search(r'Hojas a dos caras impresas en blanco y negro.*?<td[^>]*>\s*([\d,.]+)\s*<', html_snippet, re.I | re.DOTALL)
if two_sided_printed:
    print("Printed:", two_sided_printed.group(1))
