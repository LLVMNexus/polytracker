#ifndef POLYTRACKER_OUTPUT
#define POLYTRACKER_OUTPUT
#include "polytracker/logging.h"
void output(const std::string& forest_path, const std::string& db_path, RuntimeInfo* runtime_info, const size_t& current_thread, const dfsan_label& last_label);
void output(const std::string& db_path, RuntimeInfo* runtime_info, const size_t& current_thread, const dfsan_label& last_label);
#endif