#! /usr/bin/env bash

blender plate-scene.blend -b -P randomize-plate.py -- --number 10000
