#!/usr/bin/env python3

"""Constants used by initialize.py when executed.

"""
FAVICON_URL = "https://raw.githubusercontent.com/jupyterhub/jupyterhub/master/share/jupyterhub/static/favicon.ico"

JHUB_URL = 'git+https://github.com/tom-henrich/sptoolkit.git'

PROGRESS_HTML = """
<html>
<head>
    <title>The SAS Programmers Toolkit</title>
</head>
<body>
  <meta http-equiv="refresh" content="30" >
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width">
  <img class="logo" src="https://raw.githubusercontent.com/tom-henrich/sptoolkit/master/docs/images/jupyterhub_logo.png">
  <div class="loader center"></div>
  <div class="center main-msg">Please wait while your Hub is building...</div>
  <div class="center logs-msg">Click the button below to see the logs</div>
  <div class="center tip" >Tip: to update the logs, refresh the page</div>
  <button class="logs-button center" onclick="window.location.href='/logs'">View logs</button>
</body>

  <style>
    button:hover {
      background: grey;
    }

    .logo {
      width: 150px;
      height: auto;
    }
    .center {
      margin: 0 auto;
      margin-top: 50px;
      text-align:center;
      display: block;
    }
    .main-msg {
      font-size: 30px;
      font-weight: bold;
      color: grey;
      text-align:center;
    }
    .logs-msg {
      font-size: 15px;
      color: grey;
    }
    .tip {
      font-size: 13px;
      color: grey;
      margin-top: 10px;
      font-style: italic;
    }
    .logs-button {
      margin-top:15px;
      border: 0;
      color: white;
      padding: 15px 32px;
      font-size: 16px;
      cursor: pointer;
      background: #f5a252;
    }
    .loader {
      width: 150px;
      height: 150px;
      border-radius: 90%;
      border: 7px solid transparent;
      animation: spin 2s infinite ease;
      animation-direction: alternate;
    }
    @keyframes spin {
      0% {
        transform: rotateZ(0deg);
        border-top-color: #f17c0e
      }
      100% {
        transform: rotateZ(360deg);
        border-top-color: #fce5cf;
      }
    }
  </style>
</head>
<html>

"""
